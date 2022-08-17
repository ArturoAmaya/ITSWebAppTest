from fastapi_health import health
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles

router = APIRouter()

def sample_health_check():
    return True

# TODO add addition health checks to health() call
router.add_api_route("/health", health([sample_health_check]), name="health-check", tags=["health"])


from fastapi import HTTPException, Request, Response, APIRouter, Depends
from typing import Any
from starlette.responses import RedirectResponse

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from pathlib import Path
import uuid
from app.config.environment import get_settings

from fastapi_redis_session import deleteSession, getSessionId, getSessionStorage, setSession, SessionStorage

from fastapi_redis_session.config import basicConfig

from saml2 import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
    entity,
)

from saml2.config import Config as Saml2Config
from saml2.client import Saml2Client

BASE_PATH = Path(__file__).parent.resolve()

_SETTINGS = get_settings()

basicConfig(
    sessionIdGenerator=lambda : _SETTINGS.SSO_REDIS_SESSION_PREFIX + uuid.uuid4().hex,
    redisURL=_SETTINGS.REDIS_URL
    )

def setSession(response: Response, session: Any, sessionStorage: SessionStorage) -> str:
    sessionId = sessionStorage.genSessionId()
    sessionStorage[sessionId] = session
    response.set_cookie("ssid", sessionId, httponly=True, secure=True, expires=3000)
    return sessionId

def get_saml_client():
    CONFIG = {
            'entityid': _SETTINGS.SSO_IDP_ENTITY_ID,
            'service': {
                'sp': {
                    'endpoints': {
                        "assertion_consumer_service": [
							(_SETTINGS.SSO_SP_ENTITY_ID, 
							BINDING_HTTP_POST,
							),
						],
                        "single_sign_on_service": [
                            (
                                _SETTINGS.SSO_IDP_LOGIN_URL,
                                BINDING_HTTP_POST,
                            ),
                        ],
                        "single_logout_service": [
                            (
                                _SETTINGS.SSO_IDP_LOGOUT_URL,
                                BINDING_HTTP_POST,
                            ),
                        ],
                    },
					"requestedAuthnContext": {
						"authn_context_class_ref": [
							"urn:mace:ucsd.edu:sso:ad",
							],
						},
                    "required_attributes": ['urn:mace:ucsd.edu:sso:ad:username'],
                    "metadata_key_usage" : "both",
                    "enc_cert": "use",                               
                    'allow_unsolicited': True,                              
                    'authn_requests_signed': False,
                    'logout_requests_signed': False,
                    'want_assertions_signed': True,
                    'want_response_signed': False,
                },
            },        
            "key_file": "app/config/sp-key.pem",        
            "cert_file": "app/config/sp-cert.pem",
            "xmlsec_binary": '/usr/bin/xmlsec1',
            "metadata": {
                "local": ["app/config/sp.xml"],
            },        
            'encryption_keypairs': [
            {
                "key_file": "app/config/sp-key.pem",        
                "cert_file": "app/config/sp-cert.pem",
            },
            ],
            "organization": {
                "name": ["Academic Technology Innovation"],
                "display_name": ["Academic Technology Innovation"],
                "url": "https://ucsd.edu"
            },
            "contact_person": [
                {
                    "mail": "its-academictechinnovation@ucsd.edu"
                }
            ]
    }
    spConfig = Saml2Config()
    spConfig.load(CONFIG)
    spConfig.allow_unknown_attributes = True
    saml_client = Saml2Client(config=spConfig)
    return saml_client

@router.get('/saml/login', name="saml:login")
async def saml_login(request: Request):
    saml_client = get_saml_client()
    reqid, info = saml_client.prepare_for_authenticate()

    redirect_url = None
    # Select the IdP URL to send the AuthN request to
    for key, value in info['headers']:
        if key == 'Location':
            redirect_url = value
    response = RedirectResponse(redirect_url)
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response

"""
@router.get('/saml/logout', name="saml:logout")
async def saml_logout(request: Request, sessionId: str = Depends(getSessionId), 
sessionStorage: SessionStorage = Depends(getSessionStorage)):
  req = await prepare_from_fastapi_request(request)
  auth = OneLogin_Saml2_Auth(req, get_saml_settings(request))
  callback_url = auth.logout()
  response = RedirectResponse(url=callback_url)
  deleteSession(sessionId, sessionStorage)
  response.delete_cookie(key="ssid")
  return response

@router.post('/saml/callback', name="saml:callback")
async def saml_login_callback(request: Request, response: Response, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    req = await prepare_from_fastapi_request(request, True)
    auth = OneLogin_Saml2_Auth(req, get_saml_settings(request))
    auth.process_response() # Process IdP response
    errors = auth.get_errors() # This method receives an array with the errors
    if len(errors) == 0:
        if not auth.is_authenticated(): # This check if the response was ok and the user data retrieved or not (user authenticated)
            return "user Not authenticated"
        else:
            attributes = auth.get_attributes()

            user_login_json = {
              "username":attributes['urn:mace:ucsd.edu:sso:ad:username'][0],
              "role":"student",
              "pid": "U0000000"
            }

            

            setSession(response, user_login_json, sessionStorage)

            if 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
                response_url = req['post_data']['RelayState']
            else:
                response_url = request.base_url
                
            response = RedirectResponse(response_url)
            response.status_code = 302
            
            return response
    else:
        print("Error when processing SAML Response: %s %s" % (', '.join(errors), auth.get_last_error_reason()))
        return "Error in callback"
    
@router.get('/saml/metadata', name="saml:metadata")
async def saml_metadata(request: Request):
  req = await prepare_from_fastapi_request(request)
  auth = OneLogin_Saml2_Auth(req, get_saml_settings(request))
  saml_settings = auth.get_settings()
  metadata = saml_settings.get_sp_metadata()
  errors = saml_settings.validate_metadata(metadata)
  if len(errors) == 0:
    return Response(content=metadata, media_type="application/xml")
  else:
    print("Error found on Metadata: %s" % (', '.join(errors)))
    raise HTTPException(500, "Error in SP metadata.")
"""

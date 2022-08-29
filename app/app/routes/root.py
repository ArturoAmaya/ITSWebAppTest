from fastapi_health import health
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles

router = APIRouter()

def sample_health_check():
    return True

# TODO add addition health checks to health() call
router.add_api_route("/health", health([sample_health_check]), name="health-check", tags=["health"])


from fastapi import HTTPException, Request, Response, APIRouter, Depends, Form
from typing import Any
from starlette.responses import RedirectResponse

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

def get_saml_client(request: Request = Depends(Request)):

    callback_url = str(request.url_for("saml:callback"))

    print(callback_url)

    # if local, it'll point to      https://localhost:8080/saml/callback
    #https://its-fztm633.ad.ucsd.edu:8080/saml/callback


    CONFIG = {
            'entityid': _SETTINGS.SSO_SP_ENTITY_ID,
            'service': {
              'sp': {
                'endpoints': {
                  "assertion_consumer_service": [
                    (request.url_for("saml:callback"), BINDING_HTTP_POST)
                  ],
                  "single_logout_service": [
                    (request.url_for("saml:logout"), BINDING_HTTP_REDIRECT)
                  ]
                },
                "requested_authn_context": {
                  "authn_context_class_ref": [
                    "urn:mace:ucsd.edu:sso:ad",
                    "urn:mace:ucsd.edu:sso:actsso",
                    "urn:mace:ucsd.edu:sso:studentsso",
                    ],
                  },
                    "required_attributes": ['urn:mace:ucsd.edu:sso:ad:username'],
                    "metadata_key_usage" : "both",
                    "enc_cert": "use",                               
                    'allow_unsolicited': True,                              
                    'authn_requests_signed': True,
                    'logout_requests_signed': True,
                    'want_assertions_signed': True,
                    'want_response_signed': True,
                    'allow_unknown_attributes': True
                },
            },
            "metadata": {
                "remote": [
                  {
                    "url": "https://a5-stage.ucsd.edu/a5-stage-metadata-with-slo-signed.xml"
                    }
                ]
            },      
            "key_file": "app/config/sp-key.pem",        
            "cert_file": "app/config/sp-cert.pem",
            "xmlsec_binary": '/usr/bin/xmlsec1',        
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

def validateRelayState(RelayState):
    # TODO: validate that URL is plausible for our website better
    if(_SETTINGS.BASE_PATH in RelayState):
        return True
    else:
        return False

@router.get('/saml/login', name="saml:login")
async def saml_login(request: Request):

    RelayState = ""

    if('target' in request.query_params):
        RelayState = request.query_params['target']

    saml_client = get_saml_client(request)
    reqid, info = saml_client.prepare_for_authenticate(relay_state = RelayState)

    redirect_url = None
    # Select the IdP URL to send the AuthN request to
    for key, value in info['headers']:
        if key == 'Location':
            redirect_url = value
    response = RedirectResponse(redirect_url)
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response

@router.get('/saml/logout', name="saml:logout")
async def saml_logout(request: Request, sessionId: str = Depends(getSessionId), 
sessionStorage: SessionStorage = Depends(getSessionStorage)):
	# Determine IDP logout url
	saml_client = get_saml_client(request)
	entity_id = list(saml_client.metadata.with_descriptor("idpsso").keys())[0]
	bindings_slo_supported = saml_client.metadata.single_logout_service(entity_id=entity_id, typ="idpsso")
	logout_url = bindings_slo_supported[BINDING_HTTP_REDIRECT][0]["location"]

	print(logout_url)

	logout_url="https://a5-stage.ucsd.edu/tritON/profile/Logout"

	# Clear local session data
	deleteSession(sessionId, sessionStorage)

	response = RedirectResponse(url=logout_url)
	response.delete_cookie(key="ssid")
	return response

@router.post('/saml/callback', name="saml:callback")
async def saml_login_callback(request: Request, response: Response, sessionStorage: SessionStorage = Depends(getSessionStorage), SAMLResponse = Form(...), RelayState = Form(None)):
    saml_client = get_saml_client(request)
    authn_response = saml_client.parse_authn_request_response(
        SAMLResponse,
        entity.BINDING_HTTP_POST)
    attributes = authn_response.ava

    print(attributes)
    user_login_json = {
        "username":attributes['urn:mace:ucsd.edu:sso:ad:username'][0],
    }

    # handles where to go after callback
    if RelayState is not None and RelayState != "" and validateRelayState(RelayState):
        response_url = RelayState # if login is called by a protected route, will go to this page when logged in
    else:
        # will go to root URL if login is called directly. feel free to change
        # currently doesn't lead anywhere, as saml/login isn't meant to be called directly
        response_url = str(request.base_url) + _SETTINGS.BASE_PATH[1:]
    
    response = RedirectResponse(response_url)
    response.status_code = 302
    setSession(response, user_login_json, sessionStorage) # needs to be after response is initialized
    return response
    
@router.get('/saml/metadata', name="saml:metadata")
async def saml_metadata(request: Request):
    # to do: dynamically generate this
    f = open("app/config/sp.xml", "r")
    data = f.read()
    return Response(content=data, media_type="application/xml")

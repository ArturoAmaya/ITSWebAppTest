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




def get_saml_settings(request: Request = Depends(Request)): 
    return {
        "strict": False, # can set to True to see problems such as Time skew/drift
        "debug": True,
        "idp": {
            "entityId": _SETTINGS.SSO_IDP_ENTITY_ID,
            "singleSignOnService": {
            "url": _SETTINGS.SSO_LOGIN_URL,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
            "url": _SETTINGS.SSO_LOGOUT_URL,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "x509cert": _SETTINGS.SSO_SECRET_CERT,
            "privateKey": ""
        },
        "sp": {
            "entityId": _SETTINGS.SSO_SP_ENTITY_ID,
            "assertionConsumerService": {
            "url": request.url_for("saml:callback"),
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
            "x509cert": "",
            "privateKey": ""
        },
        "security": {
            "nameIdEncrypted": True,
        "requestedAuthnContext": ["urn:mace:ucsd.edu:sso:ad"],
            "authnRequestsSigned": False,
            "logoutRequestSigned": False,
            "logoutResponseSigned": False,
            "signMetadata": True,
            "wantMessagesSigned": True,
            "wantAssertionsSigned": True,
            "wantNameId" : False,
            "wantNameIdEncrypted": False,
            "wantAssertionsEncrypted": False,
            "allowSingleLabelDomains": False,
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256"
        },
        "contactPerson": {
            "technical": {
                "givenName": "Datahub Team",
                "emailAddress": "datahub@ucsd.edu"
            },
            "support": {
                "givenName": "Datahub Team",
                "emailAddress": "datahub@ucsd.edu"
            }
        },
        "organization": {
            "en-US": {
                "name": "UCSD",
                "displayname": "University of California, San Diego",
                "url": "https://ucsd.edu"
            }
        }
    }

async def prepare_from_fastapi_request(request: Request, debug=False):
  form_data = await request.form()
  rv = {
    "http_host": request.client.host,
    "server_port": request.url.port,
    "script_name": request.url.path,
    "post_data": { },
    "get_data": { }
    # Advanced request options
    # "https": "",
    # "request_uri": "",
    # "query_string": "",
    # "validate_signature_from_qs": False,
    # "lowercase_urlencoding": False
  }
  if (request.query_params):
    rv["get_data"] = request.query_params,
  if "SAMLResponse" in form_data:
    SAMLResponse = form_data["SAMLResponse"]
    rv["post_data"]["SAMLResponse"] = SAMLResponse
  if "RelayState" in form_data:
    RelayState = form_data["RelayState"]
    rv["post_data"]["RelayState"] = RelayState
  return rv

@router.get('/saml/login', name="saml:login")
async def saml_login(request: Request):
  req = await prepare_from_fastapi_request(request)
  auth = OneLogin_Saml2_Auth(req, get_saml_settings(request))
  callback_url = auth.login(return_to=request.url_for('movies:get-movies')) # TODO figure out how to capture where we originally came from
  response = RedirectResponse(url=callback_url)
  return response

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
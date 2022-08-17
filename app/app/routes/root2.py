import json
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse, PlainTextResponse
from fastapi import Request

from saml2 import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
    entity,
)

from saml2.config import Config as Saml2Config
from saml2.client import Saml2Client

from app.config.environment import get_settings

_SETTINGS = get_settings()

def saml_client_for(idp_name=None):

    CONFIG = {
            'entityid': _SETTINGS.SSO_IDP_ENTITY_ID,
            'service': {
                'sp': {
                    'endpoints': {
                        "assertion_consumer_service": [_SETTINGS.SSO_SP_ENTITY_ID],
                        "single_sign_on_service": [
                            (
                                _SETTINGS.SSO_IDP_LOGIN_URL,
                                BINDING_HTTP_REDIRECT,
                            ),
                        ],
                        "single_logout_service": [
                            (
                                _SETTINGS.SSO_IDP_LOGOUT_URL,
                                BINDING_HTTP_REDIRECT,
                            ),
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

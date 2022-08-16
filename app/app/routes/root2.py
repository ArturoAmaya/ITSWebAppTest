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
from saml2.client import Saml2Client
from saml2.s_utils import rndstr
from saml2.config import Config as Saml2Config

import requests
import logging

from app.config.environment import get_settings

sso_router = sso = APIRouter()

uid2user = {}           # global variable to keep user object

_SETTINGS = get_settings()

metadata_url_for = {
    'okta': 'https://saml-bird.daad.com/saml2/idp/metadata.php',
    }


def saml_client_for(idp_name=None):
    '''
    Given the name of an IdP, return a configuation.
    The configuration is a hash for use by saml2.config.Config
    '''

    if idp_name not in metadata_url_for:
        raise Exception("Settings for IDP '{}' not found".format(idp_name))
    rv = requests.get(metadata_url_for[idp_name])

    settings = {
        'entityid': _SETTINGS.SSO_IDP_ENTITY_ID,
        'service': {
            'sp': {
                'endpoints': {
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
                "required_attributes": ['displayName','mail',],
                "metadata_key_usage" : "both",
                "enc_cert": "use",                               
                'allow_unsolicited': True,                              
                'authn_requests_signed': False,
                'logout_requests_signed': False,
                'want_assertions_signed': True,
                'want_response_signed': False,
            },
        },        
        "key_file": "/code/app/app/config/sp-key.pem",        
        "cert_file": "/code/app/app/config/sp-cert.pem",
        "xmlsec_binary": '/usr/bin/xmlsec1',        
        'encryption_keypairs': [
          {
            "key_file": "/code/app/app/config/sp-key.pem",        
            "cert_file": "/code/app/app/config/sp-cert.pem",
          },
        ],
    }
    spConfig = Saml2Config()
    spConfig.load(settings)

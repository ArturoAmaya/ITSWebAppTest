from saml2 import BINDING_HTTP_REDIRECT
from app.config.environment import get_settings
_SETTINGS = get_settings()

CONFIG = {
        'entityid': _SETTINGS.SSO_IDP_ENTITY_ID,
        'service': {
            'sp': {
                'endpoints': {
                    "assertion_consumer_service": _SETTINGS.SSO_SP_ENTITY_ID,
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

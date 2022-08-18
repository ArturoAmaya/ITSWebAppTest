from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from app.config.environment import get_settings
_SETTINGS = get_settings()

# this config is used to generate sp metadata

# run this to generate metadata:
# python3 app/config/make_metadata.py app/config/config.py > app/config/sp.xml

# this should be about the same as the one you have defined in root.py
# but you can't use request.url_for() here, so use .env settings instead.
# set SSO related URLs to the URLs relevant to your environment

CONFIG = {
            'entityid': _SETTINGS.SSO_SP_ENTITY_ID,
            'service': {
              'sp': {
                'endpoints': {
                  "assertion_consumer_service": [
                    (_SETTINGS.SSO_SP_ENTITY_ID + _SETTINGS.BASE_PATH + "/saml/callback", BINDING_HTTP_POST)
                  ],
                  "single_logout_service": [
                    (_SETTINGS.SSO_SP_ENTITY_ID + _SETTINGS.BASE_PATH + "/saml/logout", BINDING_HTTP_REDIRECT)
                  ]
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
                    'allow_unknown_attributes': True
                },
            },
            "metadata": {
                "local": [
                    "app/config/idp.xml",  
                ],
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

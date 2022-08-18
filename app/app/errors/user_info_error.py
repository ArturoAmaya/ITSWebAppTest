from starlette.requests import Request
from starlette.responses import RedirectResponse
import urllib.parse

class UserInfoException(Exception):
    def __init__(self):
        message = "You aren't logged in! Redirecting to the login page..."

async def get_user_info_exception_handler(request: Request, exc: UserInfoException):

	target = urllib.parse.quote_plus(str(request.url))

	return(
	RedirectResponse(url=f"/python-webapp-archetype/saml/login?target={target}")
	)

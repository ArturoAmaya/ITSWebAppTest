from starlette.requests import Request
from starlette.responses import RedirectResponse
import urllib.parse

from app.config.environment import get_settings
_SETTINGS = get_settings()

class UserInfoException(Exception):
    def __init__(self):
        message = "You aren't logged in! Redirecting to the login page..."

async def get_user_info_exception_handler(request: Request, exc: UserInfoException):

	target = urllib.parse.quote_plus(str(request.url))

	BASE_PATH = _SETTINGS.BASE_PATH

	return(
	RedirectResponse(url=f"{BASE_PATH}/saml/login?target={target}")
	)

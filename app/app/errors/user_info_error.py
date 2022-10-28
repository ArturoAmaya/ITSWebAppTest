from starlette.requests import Request
from starlette.responses import RedirectResponse
import urllib.parse

from app.config.environment import get_settings
class UserInfoException(Exception):
    def __init__(self):
        message = "You aren't logged in! Redirecting to the login page..."

async def get_user_info_exception_handler(request: Request, exc: UserInfoException):

	target = urllib.parse.quote_plus(str(request.url))
	login_url = str(request.url_for("saml:login"))
	return RedirectResponse(url=f"{login_url}?target={target}")
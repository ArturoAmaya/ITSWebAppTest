from app.app.errors.user_info_error import UserInfoException
from fastapi_redis_session import getSession, SessionStorage, getSessionStorage
from fastapi import Depends

async def get_user_info(request, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    session_id = request.cookies.get("ssid")
    if(session_id is not None):
        session = getSession(request, SessionStorage())
        return(session)
    raise UserInfoException

from fastapi import HTTPException, Request
from fastapi.applications import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from toolz import pipe

from app.app.errors.http_error import http_error_handler, validation_error_handler
from app.app.routes import register_routers as register_routers
from app.config.environment import Settings
from app.infrastructure.database.db import create_db_and_tables, init_db

class TemplateMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        templates = Jinja2Templates(directory="app/app/templates")
        request.state.templates = templates
        # process the request and get the response    
        response = await call_next(request)
        
        return response

    

def create_instance(settings: Settings) -> FastAPI:
    return FastAPI(
        docs_url=settings.BASE_PATH + '/docs', redoc_url=None, 
        openapi_url=settings.BASE_PATH + '/openapi.json',
        debug=settings.WEB_APP_DEBUG,
        title=settings.WEB_APP_TITLE,
        description=settings.WEB_APP_DESCRIPTION,
        version=settings.WEB_APP_VERSION,
        prefix=settings.BASE_PATH
    )


def init_database(app: FastAPI) -> FastAPI:
    # TODO init databases if applicable
    init_db()
    return app


def register_events(app: FastAPI) -> FastAPI:
    # TODO add events if applicable
    app.on_event("startup")(create_db_and_tables) # This event can be removed if not seeding a database
    return app


def register_middleware(app: FastAPI) -> FastAPI:
    # TODO register middleware if applicable

    app.add_middleware(TemplateMiddleware)
    
    return app

def register_exception_handlers(app: FastAPI) -> FastAPI:
    # TODO register exception handlers if applicable
    # Modify HttpExceptions to follow API guidelines
    # app.add_exception_handler(HTTPException, http_error_handler)
    # app.add_exception_handler(StarletteHTTPException, http_error_handler)
    # app.add_exception_handler(RequestValidationError, validation_error_handler)
    return app
    

def init_app(settings: Settings) -> FastAPI:
    app: FastAPI = pipe(
        settings,
        create_instance,
        init_database,
        register_events,
        register_middleware,
        register_routers,
        register_exception_handlers,
    )
    app.mount(settings.BASE_PATH + "/static", StaticFiles(directory="app/static"), name="static")
    return app

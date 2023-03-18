from fastapi import APIRouter
from fastapi.applications import FastAPI

from app.app.routes import movies, root, whatif
from app.config.environment import get_settings
from app.domain.models.errors import APIMErrorResponse, ErrorResponse

def register_routers(app: FastAPI) -> FastAPI:
    settings = get_settings()
    app.router.prefix=settings.BASE_PATH
    app.router.responses |= {400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 401: {"model": APIMErrorResponse}, 422: {"model": APIMErrorResponse}, 500: {"model": ErrorResponse}}
    app.include_router(root.router)
    app.include_router(movies.router, tags=["movies"], prefix="/movies")
    app.include_router(whatif.router, tags=["whatif"], prefix="/whatif")
    # TODO add additional routers defined in separate route .py files
    return app
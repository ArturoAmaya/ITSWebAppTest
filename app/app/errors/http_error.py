from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.domain.models.errors import ErrorResponse

# Restructure errors to meet the REST API guidelines
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    headers = getattr(exc, 'headers', None)
    return JSONResponse(ErrorResponse(message = exc.detail, code = exc.status_code).dict(exclude_none=True), status_code=exc.status_code, headers=headers)

async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    headers = getattr(exc, 'headers', None)
    errors = exc.errors()
    for e in errors:
        e["message"] = e.pop('msg')
    return JSONResponse(ErrorResponse(code = status.HTTP_422_UNPROCESSABLE_ENTITY, errors=errors).dict(exclude_none=True), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, headers=headers)
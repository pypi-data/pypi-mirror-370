from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from agent.exception.exception_constants import exception_constants
from agent.response.common_response import CommonResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if exc.detail else "An error occurred"
    code = exc.status_code if exc.status_code else status.HTTP_400_BAD_REQUEST
    return JSONResponse(
        status_code=code,
        content=CommonResponse(
            code=exception_constants.HTTP_SYSTEM_EXCEPTION,
            reason=str(detail)
        ).json()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=CommonResponse(
            code=exception_constants.ROUTE_VALIDATION_EXCEPTION,
            reason=str(exc.errors())
        ).json()
    )

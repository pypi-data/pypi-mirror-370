import logging
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from maleo.soma.enums.logging import LogLevel
from maleo.soma.exceptions import Error
from maleo.soma.schemas.response import (
    UnauthorizedResponseSchema,
    UnprocessableEntityResponseSchema,
    InternalServerErrorResponseSchema,
    OTHER_RESPONSES,
)
from maleo.soma.schemas.service import ServiceContext


def authentication_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        content=UnauthorizedResponseSchema().model_dump(mode="json"),
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        content=UnprocessableEntityResponseSchema(
            other=jsonable_encoder(exc.errors())
        ).model_dump(mode="json"),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        content=UnprocessableEntityResponseSchema(other=exc.errors()).model_dump(
            mode="json"
        ),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code in OTHER_RESPONSES:
        return JSONResponse(
            content=OTHER_RESPONSES[exc.status_code]["model"](
                other=str(exc)
            ).model_dump(  # type: ignore
                mode="json"
            ),  # type: ignore
            status_code=exc.status_code,
        )

    return JSONResponse(
        content=InternalServerErrorResponseSchema(other=str(exc)).model_dump(
            mode="json"
        ),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def maleo_exception_handler(request: Request, exc: Error):
    service_context = ServiceContext.from_env()
    logger = logging.getLogger(
        f"{service_context.environment} - {service_context.key} - application"
    )
    if exc.spec.status_code in OTHER_RESPONSES:
        content = OTHER_RESPONSES[exc.spec.status_code]["model"](
            code=exc.spec.code,
            message=exc.spec.message,
            description=exc.spec.description,
        )
        if exc.details is not None:
            content.other = exc.details
        exc.operation_schema.log(logger, level=LogLevel.ERROR)
        return JSONResponse(
            content=content.model_dump(mode="json"),  # type: ignore
            status_code=exc.spec.status_code,
        )

    exc.operation_schema.log(logger, level=LogLevel.ERROR)
    return JSONResponse(
        content=InternalServerErrorResponseSchema(
            code=exc.spec.code,
            message=exc.spec.message,
            description=exc.spec.description,
            other=exc.details,
        ).model_dump(mode="json"),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

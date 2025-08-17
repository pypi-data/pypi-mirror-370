import http.client
from pydantic import BaseModel, Field
from typing import TypeVar
from maleo.soma.enums.error import Error as ErrorType
from maleo.soma.mixins.general import StatusCode
from .descriptor import (
    ErrorDescriptorSchema,
    BadRequestErrorDescriptorSchema,
    UnauthorizedErrorDescriptorSchema,
    ForbiddenErrorDescriptorSchema,
    NotFoundErrorDescriptorSchema,
    MethodNotAllowedErrorDescriptorSchema,
    ConflictErrorDescriptorSchema,
    UnprocessableEntityErrorDescriptorSchema,
    TooManyRequestsErrorDescriptorSchema,
    InternalServerErrorDescriptorSchema,
    DatabaseErrorDescriptorSchema,
    NotImplementedErrorDescriptorSchema,
    BadGatewayErrorDescriptorSchema,
    ServiceUnavailableErrorDescriptorSchema,
)


class ErrorTypeMixin(BaseModel):
    type: ErrorType = Field(..., description="Error type")


class ErrorSpecSchema(ErrorDescriptorSchema, StatusCode, ErrorTypeMixin):
    pass


ErrorSpecSchemaT = TypeVar("ErrorSpecSchemaT", bound=ErrorSpecSchema)


class BadRequestErrorSpecSchema(BadRequestErrorDescriptorSchema, ErrorSpecSchema):
    type: ErrorType = ErrorType.BAD_REQUEST
    status_code: int = http.client.BAD_REQUEST


class UnauthorizedErrorSpecSchema(UnauthorizedErrorDescriptorSchema, ErrorSpecSchema):
    type: ErrorType = ErrorType.UNAUTHORIZED
    status_code: int = http.client.UNAUTHORIZED


class ForbiddenErrorSpecSchema(ForbiddenErrorDescriptorSchema, ErrorSpecSchema):
    type: ErrorType = ErrorType.FORBIDDEN
    status_code: int = http.client.FORBIDDEN


class NotFoundErrorSpecSchema(NotFoundErrorDescriptorSchema, ErrorSpecSchema):
    type: ErrorType = ErrorType.NOT_FOUND
    status_code: int = http.client.NOT_FOUND


class MethodNotAllowedErrorSpecSchema(
    MethodNotAllowedErrorDescriptorSchema, ErrorSpecSchema
):
    type: ErrorType = ErrorType.METHOD_NOT_ALLOWED
    status_code: int = http.client.METHOD_NOT_ALLOWED


class ConflictErrorSpecSchema(ConflictErrorDescriptorSchema, ErrorSpecSchema):
    type: ErrorType = ErrorType.CONFLICT
    status_code: int = http.client.CONFLICT


class UnprocessableEntityErrorSpecSchema(
    UnprocessableEntityErrorDescriptorSchema, ErrorSpecSchema
):
    type: ErrorType = ErrorType.UNPROCESSABLE_ENTITY
    status_code: int = http.client.UNPROCESSABLE_ENTITY


class TooManyRequestsErrorSpecSchema(
    TooManyRequestsErrorDescriptorSchema, ErrorSpecSchema
):
    type: ErrorType = ErrorType.TOO_MANY_REQUESTS
    status_code: int = http.client.TOO_MANY_REQUESTS


class InternalServerErrorSpecSchema(
    InternalServerErrorDescriptorSchema, ErrorSpecSchema
):
    type: ErrorType = ErrorType.INTERNAL_SERVER_ERROR
    status_code: int = http.client.INTERNAL_SERVER_ERROR


class DatabaseErrorSpecSchema(
    DatabaseErrorDescriptorSchema, InternalServerErrorSpecSchema
):
    type: ErrorType = ErrorType.DATABASE_ERROR


class NotImplementedErrorSpecSchema(
    NotImplementedErrorDescriptorSchema, ErrorSpecSchema
):
    type: ErrorType = ErrorType.NOT_IMPLEMENTED
    status_code: int = http.client.NOT_IMPLEMENTED


class BadGatewayErrorSpecSchema(BadGatewayErrorDescriptorSchema, ErrorSpecSchema):
    type: ErrorType = ErrorType.BAD_GATEWAY
    status_code: int = http.client.BAD_GATEWAY


class ServiceUnavailableErrorSpecSchema(
    ServiceUnavailableErrorDescriptorSchema, ErrorSpecSchema
):
    type: ErrorType = ErrorType.SERVICE_UNAVAILABLE
    status_code: int = http.client.SERVICE_UNAVAILABLE

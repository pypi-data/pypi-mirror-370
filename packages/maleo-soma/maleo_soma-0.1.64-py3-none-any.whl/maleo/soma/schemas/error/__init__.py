from pydantic import BaseModel, Field
from typing import Any, Optional, TypeVar
from .metadata import ErrorMetadataSchema
from .spec import (
    ErrorSpecSchema,
    BadRequestErrorSpecSchema,
    UnauthorizedErrorSpecSchema,
    ForbiddenErrorSpecSchema,
    NotFoundErrorSpecSchema,
    MethodNotAllowedErrorSpecSchema,
    ConflictErrorSpecSchema,
    UnprocessableEntityErrorSpecSchema,
    TooManyRequestsErrorSpecSchema,
    InternalServerErrorSpecSchema,
    DatabaseErrorSpecSchema,
    NotImplementedErrorSpecSchema,
    BadGatewayErrorSpecSchema,
    ServiceUnavailableErrorSpecSchema,
)


# ! Do not instantiate and use this class
# * This class is created for future type override
class AnyErrorMixin(BaseModel):
    error: Any = Field(..., description="Error.")


class NoErrorMixin(AnyErrorMixin):
    error: None = None


class ErrorSchema(
    ErrorMetadataSchema,
    ErrorSpecSchema,
):
    pass


ErrorSchemaT = TypeVar("ErrorSchemaT", bound=ErrorSchema)


class ErrorMixin(AnyErrorMixin):
    error: ErrorSchema = Field(..., description="Error.")


class OptionalErrorMixin(AnyErrorMixin):
    error: Optional[ErrorSchema] = Field(None, description="Error. (Optional)")


class BadRequestErrorSchema(BadRequestErrorSpecSchema, ErrorSchema):
    pass


class UnauthorizedErrorSchema(UnauthorizedErrorSpecSchema, ErrorSchema):
    pass


class ForbiddenErrorSchema(ForbiddenErrorSpecSchema, ErrorSchema):
    pass


class NotFoundErrorSchema(NotFoundErrorSpecSchema, ErrorSchema):
    pass


class MethodNotAllowedErrorSchema(MethodNotAllowedErrorSpecSchema, ErrorSchema):
    pass


class ConflictErrorSchema(ConflictErrorSpecSchema, ErrorSchema):
    pass


class UnprocessableEntityErrorSchema(UnprocessableEntityErrorSpecSchema, ErrorSchema):
    pass


class TooManyRequestsErrorSchema(TooManyRequestsErrorSpecSchema, ErrorSchema):
    pass


class InternalServerErrorSchema(InternalServerErrorSpecSchema, ErrorSchema):
    pass


class DatabaseErrorSchema(DatabaseErrorSpecSchema, InternalServerErrorSchema):
    pass


class NotImplementedErrorSchema(NotImplementedErrorSpecSchema, ErrorSchema):
    pass


class BadGatewayErrorSchema(BadGatewayErrorSpecSchema, ErrorSchema):
    pass


class ServiceUnavailableErrorSchema(ServiceUnavailableErrorSpecSchema, ErrorSchema):
    pass

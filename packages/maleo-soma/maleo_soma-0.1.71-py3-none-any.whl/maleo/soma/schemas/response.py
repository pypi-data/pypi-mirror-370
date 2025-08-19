import json
from base64 import b64decode, b64encode
from charset_normalizer import from_bytes
from fastapi import status
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    ValidationInfo,
)
from typing import Dict, Generic, List, Optional, Tuple, Type, TypedDict, Union
from maleo.soma.mixins.general import Success, Descriptor, OptionalOther
from maleo.soma.schemas.data import (
    DataT,
    AnyDataMixin,
    NoDataMixin,
    SingleDataMixin,
    MultipleDataMixin,
    OptionalSingleDataMixin,
    OptionalMultipleDataMixin,
)
from maleo.soma.schemas.error.descriptor import (
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
from maleo.soma.schemas.pagination import PaginationT
from maleo.soma.schemas.result.descriptor import (
    AnyDataResultDescriptorSchema,
    NoDataResultDescriptorSchema,
    SingleDataResultDescriptorSchema,
    OptionalSingleDataResultDescriptorSchema,
    MultipleDataResultDescriptorSchema,
    OptionalMultipleDataResultDescriptorSchema,
)
from maleo.soma.types.base import OptionalAny, OptionalString, StringToAnyDict
from .metadata import OptionalMetadataMixin, MetadataT
from .pagination import (
    AnyPaginationMixin,
    NoPaginationMixin,
    PaginationMixin,
)


class ResponseContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status_code: int = Field(..., description="Status code")
    media_type: OptionalString = Field(None, description="Media type (Optional)")
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Response's headers"
    )
    body: Union[bytes, memoryview] = Field(..., description="Content (Optional)")

    @field_serializer("body")
    def serialize_body(
        self, body: Union[bytes, memoryview]
    ) -> Union[StringToAnyDict, str]:
        """Serialize body for logging (JSON, text/* with encoding detection, or Base64 fallback)."""
        try:
            raw_bytes = bytes(body)

            # JSON case (assume UTF-8 as per RFC 8259)
            if self.media_type and "application/json" in self.media_type.lower():
                try:
                    return json.loads(raw_bytes.decode("utf-8"))
                except Exception:
                    return raw_bytes.decode("utf-8", errors="replace")

            # Text case (auto-detect encoding, covers text/html, text/plain, etc.)
            elif self.media_type and self.media_type.lower().startswith("text/"):
                detected = from_bytes(raw_bytes).best()
                return (
                    str(detected)
                    if detected
                    else raw_bytes.decode("utf-8", errors="replace")
                )

            # Unknown type → base64 encode to preserve safely
            else:
                return b64encode(raw_bytes).decode("ascii")

        except Exception as e:
            # Fallback for logging safety
            return f"<unserializable body: {str(e)}>"

    @field_validator("body", mode="before")
    def deserialize_body(cls, v, info: ValidationInfo):
        """Inverse of serialize_body: turn incoming value back into bytes."""
        media_type = info.data.get("media_type", None)

        # Already bytes or memoryview — nothing to do
        if isinstance(v, (bytes, memoryview)):
            return v

        # JSON case
        if media_type and "application/json" in media_type.lower():
            if isinstance(v, dict):
                return json.dumps(v).encode("utf-8")
            elif isinstance(v, str):
                return v.encode("utf-8")
            else:
                raise ValueError("Invalid JSON body type")

        # Text case
        if media_type and media_type.lower().startswith("text/"):
            if isinstance(v, str):
                return v.encode("utf-8")
            else:
                raise ValueError("Invalid text body type")

        # Fallback: base64
        if isinstance(v, str):
            try:
                return b64decode(v)
            except Exception:
                raise ValueError("Invalid Base64 body string")

        raise ValueError("Unsupported body type")


class ResponseContextMixin(BaseModel):
    response_context: ResponseContext = Field(..., description="Response's context")


class OptionalResponseContextMixin(BaseModel):
    response_context: Optional[ResponseContext] = Field(
        None, description="Response's context. (Optional)"
    )


class BaseResponseSchema(
    OptionalOther,
    OptionalMetadataMixin[MetadataT],
    AnyPaginationMixin,
    AnyDataMixin,
    Descriptor,
    Success,
    Generic[MetadataT],
):
    pass


class FailedResponseSchema(
    NoPaginationMixin,
    NoDataMixin,
    ErrorDescriptorSchema,
    BaseResponseSchema[None],
):
    success: bool = False
    data: None = None
    metadata: None = None
    other: OptionalAny = "Please try again later or contact administrator"


class BadRequestResponseSchema(BadRequestErrorDescriptorSchema, FailedResponseSchema):
    pass


class InvalidExpandResponseSchema(BadRequestResponseSchema):
    pass


class InvalidParameterResponseSchema(BadRequestResponseSchema):
    pass


class InvalidSystemRoleResponseSchema(BadRequestResponseSchema):
    pass


class UnauthorizedResponseSchema(
    UnauthorizedErrorDescriptorSchema, FailedResponseSchema
):
    pass


class ForbiddenResponseSchema(ForbiddenErrorDescriptorSchema, FailedResponseSchema):
    pass


class NotFoundResponseSchema(NotFoundErrorDescriptorSchema, FailedResponseSchema):
    pass


class MethodNotAllowedResponseSchema(
    MethodNotAllowedErrorDescriptorSchema, FailedResponseSchema
):
    pass


class ConflictResponseSchema(ConflictErrorDescriptorSchema, FailedResponseSchema):
    pass


class UnprocessableEntityResponseSchema(
    UnprocessableEntityErrorDescriptorSchema, FailedResponseSchema
):
    pass


class TooManyRequestsResponseSchema(
    TooManyRequestsErrorDescriptorSchema, FailedResponseSchema
):
    pass


class InternalServerErrorResponseSchema(
    InternalServerErrorDescriptorSchema, FailedResponseSchema
):
    pass


class DatabaseErrorResponseSchema(DatabaseErrorDescriptorSchema, FailedResponseSchema):
    pass


class NotImplementedResponseSchema(
    NotImplementedErrorDescriptorSchema, FailedResponseSchema
):
    pass


class BadGatewayResponseSchema(BadGatewayErrorDescriptorSchema, FailedResponseSchema):
    pass


class ServiceUnavailableResponseSchema(
    ServiceUnavailableErrorDescriptorSchema, FailedResponseSchema
):
    pass


class SuccessfulResponseSchema(
    AnyDataResultDescriptorSchema,
    BaseResponseSchema[MetadataT],
    Generic[MetadataT],
):
    success: bool = True


class NoDataResponseSchema(
    NoPaginationMixin,
    NoDataMixin,
    NoDataResultDescriptorSchema,
    SuccessfulResponseSchema[MetadataT],
    Generic[MetadataT],
):
    pass


class SingleDataResponseSchema(
    NoPaginationMixin,
    SingleDataMixin[DataT],
    SingleDataResultDescriptorSchema,
    SuccessfulResponseSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class OptionalSingleDataResponseSchema(
    NoPaginationMixin,
    OptionalSingleDataMixin[DataT],
    OptionalSingleDataResultDescriptorSchema,
    SuccessfulResponseSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class MultipleDataResponseSchema(
    PaginationMixin[PaginationT],
    MultipleDataMixin[DataT],
    MultipleDataResultDescriptorSchema,
    SuccessfulResponseSchema[MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class OptionalMultipleDataResponseSchema(
    PaginationMixin[PaginationT],
    OptionalMultipleDataMixin[DataT],
    OptionalMultipleDataResultDescriptorSchema,
    SuccessfulResponseSchema[MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class ResponseSpec(TypedDict):
    description: str
    model: Type[FailedResponseSchema]  # callable Pydantic model


OTHER_RESPONSES: Dict[int, ResponseSpec] = {
    status.HTTP_400_BAD_REQUEST: {
        "description": "Bad Request Response",
        "model": BadRequestResponseSchema,
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Unauthorized Response",
        "model": UnauthorizedResponseSchema,
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "Forbidden Response",
        "model": ForbiddenResponseSchema,
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found Response",
        "model": NotFoundResponseSchema,
    },
    status.HTTP_405_METHOD_NOT_ALLOWED: {
        "description": "Method Not Allowed Response",
        "model": MethodNotAllowedResponseSchema,
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict Response",
        "model": ConflictResponseSchema,
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Unprocessable Entity Response",
        "model": UnprocessableEntityResponseSchema,
    },
    status.HTTP_429_TOO_MANY_REQUESTS: {
        "description": "Too Many Requests Response",
        "model": TooManyRequestsResponseSchema,
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error Response",
        "model": InternalServerErrorResponseSchema,
    },
    status.HTTP_501_NOT_IMPLEMENTED: {
        "description": "Not Implemented Response",
        "model": NotImplementedResponseSchema,
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "Service Unavailable Response",
        "model": ServiceUnavailableResponseSchema,
    },
}

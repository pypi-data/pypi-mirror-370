from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from maleo.soma.enums.operation import OperationOrigin, OperationLayer, OperationTarget
from maleo.soma.types.base import OptionalStringToAnyDict


T = TypeVar("T", bound=StrEnum)


class OperationContextComponentSchema(BaseModel, Generic[T]):
    type: T = Field(..., description="Component's type")
    details: OptionalStringToAnyDict = Field(None, description="Component's details")


class OperationOriginSchema(OperationContextComponentSchema[OperationOrigin]):
    pass


class OperationOriginMixin(BaseModel):
    origin: OperationOriginSchema = Field(..., description="Operation's origin")


class OperationLayerSchema(OperationContextComponentSchema[OperationLayer]):
    pass


class OperationLayerMixin(BaseModel):
    layer: OperationLayerSchema = Field(..., description="Operation's layer")


class OperationTargetSchema(OperationContextComponentSchema[OperationTarget]):
    pass


class OperationTargetMixin(BaseModel):
    target: OperationTargetSchema = Field(..., description="Operation's target")


class OperationContextSchema(
    OperationTargetMixin, OperationLayerMixin, OperationOriginMixin
):
    pass


UTILITY_OPERATION_CONTEXT = OperationContextSchema(
    origin=OperationOriginSchema(type=OperationOrigin.UTILITY, details=None),
    layer=OperationLayerSchema(type=OperationLayer.INTERNAL, details=None),
    target=OperationTargetSchema(type=OperationTarget.INTERNAL, details=None),
)


def generate_operation_context(
    origin: OperationOrigin,
    layer: OperationLayer,
    target: OperationTarget = OperationTarget.INTERNAL,
    origin_details: OptionalStringToAnyDict = None,
    layer_details: OptionalStringToAnyDict = None,
    target_details: OptionalStringToAnyDict = None,
) -> OperationContextSchema:
    return OperationContextSchema(
        origin=OperationOriginSchema(type=origin, details=origin_details),
        layer=OperationLayerSchema(type=layer, details=layer_details),
        target=OperationTargetSchema(type=target, details=target_details),
    )


class OperationContextMixin(BaseModel):
    context: OperationContextSchema = Field(..., description="Operation's context")


class OptionalOperationContextMixin(BaseModel):
    context: Optional[OperationContextSchema] = Field(
        None, description="Operation's context. (Optional)"
    )

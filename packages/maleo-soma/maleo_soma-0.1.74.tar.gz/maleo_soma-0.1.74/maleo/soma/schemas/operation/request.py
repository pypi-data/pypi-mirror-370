from typing import Generic, Literal
from maleo.soma.enums.operation import (
    OperationType,
)
from maleo.soma.mixins.general import SuccessT
from maleo.soma.schemas.error import (
    NoErrorMixin,
    OptionalErrorMixin,
)
from maleo.soma.schemas.operation.base import BaseOperationSchema
from maleo.soma.schemas.response import ResponseContextMixin
from maleo.soma.schemas.operation.resource.action import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    ResourceOperationActionSchemaT,
)


class RequestOperationSchema(
    ResponseContextMixin,
    BaseOperationSchema[SuccessT, ResourceOperationActionSchemaT],
    Generic[SuccessT, ResourceOperationActionSchemaT],
):
    type: OperationType = OperationType.REQUEST


class FailedRequestOperationSchema(
    OptionalErrorMixin,
    RequestOperationSchema[Literal[False], ResourceOperationActionSchemaT],
    Generic[ResourceOperationActionSchemaT],
):
    success: Literal[False] = False
    summary: str = "Failed processing request"


class CreateFailedRequestOperationSchema(
    FailedRequestOperationSchema[CreateResourceOperationAction]
):
    pass


class ReadFailedRequestOperationSchema(
    FailedRequestOperationSchema[ReadResourceOperationAction]
):
    pass


class UpdateFailedRequestOperationSchema(
    FailedRequestOperationSchema[UpdateResourceOperationAction]
):
    pass


class DeleteFailedRequestOperationSchema(
    FailedRequestOperationSchema[DeleteResourceOperationAction]
):
    pass


class SuccessfulRequestOperationSchema(
    NoErrorMixin,
    RequestOperationSchema[Literal[True], ResourceOperationActionSchemaT],
    Generic[ResourceOperationActionSchemaT],
):
    success: Literal[True] = True
    summary: str = "Successfully processed request"


class CreateSuccessfulRequestOperationSchema(
    SuccessfulRequestOperationSchema[CreateResourceOperationAction]
):
    pass


class ReadSuccessfulRequestOperationSchema(
    SuccessfulRequestOperationSchema[ReadResourceOperationAction]
):
    pass


class UpdateSuccessfulRequestOperationSchema(
    SuccessfulRequestOperationSchema[UpdateResourceOperationAction]
):
    pass


class DeleteSuccessfulRequestOperationSchema(
    SuccessfulRequestOperationSchema[DeleteResourceOperationAction]
):
    pass

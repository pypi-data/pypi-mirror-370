from typing import Generic, Literal, Optional, Union, overload
from uuid import UUID
from maleo.soma.enums.operation import (
    OperationType,
    ResourceOperationCreateType,
    ResourceOperationStatusUpdateType,
    ResourceOperationType,
    ResourceOperationUpdateType,
)
from maleo.soma.mixins.general import SuccessT
from maleo.soma.schemas.authentication import (
    Authentication,
)
from maleo.soma.schemas.data import DataT
from maleo.soma.schemas.error import (
    ErrorSchema,
    NoErrorMixin,
    ErrorMixin,
)
from maleo.soma.schemas.metadata import MetadataT
from maleo.soma.schemas.operation.base import BaseOperationSchema
from maleo.soma.schemas.operation.context import OperationContextSchema
from maleo.soma.schemas.operation.result import (
    AnyOperationResultMixin,
    NoOperationResultMixin,
    OperationResultMixin,
)
from maleo.soma.schemas.operation.timestamp import OperationTimestamp
from maleo.soma.schemas.pagination import PaginationT
from maleo.soma.schemas.request import RequestContext
from maleo.soma.schemas.resource import ResourceMixin, Resource
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.types.literals.operation import (
    OptionalResourceOperationTypeLiteral,
    CreateResourceOperationTypeLiteral,
    ReadResourceOperationTypeLiteral,
    UpdateResourceOperationTypeLiteral,
    DeleteResourceOperationTypeLiteral,
)
from .action import (
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
    AllResourceOperationAction,
    ResourceOperationActionSchemaT,
    generate_resource_operation_action,
)
from .result import (
    ResourceOperationResultSchema,
    NoDataResourceOperationResult,
    CreateSingleResourceOperationResult,
    ReadSingleResourceOperationResult,
    UpdateSingleResourceOperationResult,
    DeleteSingleResourceOperationResult,
    CreateMultipleResourceOperationResult,
    ReadMultipleResourceOperationResult,
    UpdateMultipleResourceOperationResult,
    DeleteMultipleResourceOperationResult,
)


class ResourceOperationSchema(
    AnyOperationResultMixin,
    ResourceMixin,
    BaseOperationSchema[SuccessT, ResourceOperationActionSchemaT],
    Generic[SuccessT, ResourceOperationActionSchemaT],
):
    type: OperationType = OperationType.RESOURCE


class FailedResourceOperationSchema(
    NoOperationResultMixin,
    ErrorMixin,
    ResourceOperationSchema[Literal[False], ResourceOperationActionSchemaT],
    Generic[ResourceOperationActionSchemaT],
):
    success: Literal[False] = False


class CreateFailedResourceOperationSchema(
    FailedResourceOperationSchema[CreateResourceOperationAction],
):
    pass


class ReadFailedResourceOperationSchema(
    FailedResourceOperationSchema[ReadResourceOperationAction],
):
    pass


class UpdateFailedResourceOperationSchema(
    FailedResourceOperationSchema[UpdateResourceOperationAction],
):
    pass


class DeleteFailedResourceOperationSchema(
    FailedResourceOperationSchema[DeleteResourceOperationAction],
):
    pass


@overload
def generate_failed_resource_operation(
    action: CreateResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> CreateFailedResourceOperationSchema: ...
@overload
def generate_failed_resource_operation(
    action: ReadResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> ReadFailedResourceOperationSchema: ...
@overload
def generate_failed_resource_operation(
    action: UpdateResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> UpdateFailedResourceOperationSchema: ...
@overload
def generate_failed_resource_operation(
    action: DeleteResourceOperationAction,
    *,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> DeleteFailedResourceOperationSchema: ...
@overload
def generate_failed_resource_operation(
    *,
    type: CreateResourceOperationTypeLiteral,
    create_type: Optional[ResourceOperationCreateType] = ...,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> CreateFailedResourceOperationSchema: ...
@overload
def generate_failed_resource_operation(
    *,
    type: ReadResourceOperationTypeLiteral,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> ReadFailedResourceOperationSchema: ...
@overload
def generate_failed_resource_operation(
    *,
    type: UpdateResourceOperationTypeLiteral,
    update_type: Optional[ResourceOperationUpdateType] = ...,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = ...,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> UpdateFailedResourceOperationSchema: ...
@overload
def generate_failed_resource_operation(
    *,
    type: DeleteResourceOperationTypeLiteral,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> DeleteFailedResourceOperationSchema: ...
def generate_failed_resource_operation(
    action: Optional[AllResourceOperationAction] = None,
    *,
    type: OptionalResourceOperationTypeLiteral = None,
    create_type: Optional[ResourceOperationCreateType] = None,
    update_type: Optional[ResourceOperationUpdateType] = None,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None,
    service_context: ServiceContext,
    id: UUID,
    context: OperationContextSchema,
    timestamp: OperationTimestamp,
    summary: str,
    error: ErrorSchema,
    request_context: Optional[RequestContext],
    authentication: Optional[Authentication],
    resource: Resource,
) -> Union[
    CreateFailedResourceOperationSchema,
    ReadFailedResourceOperationSchema,
    UpdateFailedResourceOperationSchema,
    DeleteFailedResourceOperationSchema,
]:
    if (action is None and type is None) or (action is not None and type is not None):
        raise ValueError("Only either 'action' or 'type' must be given")

    if action is not None:
        if not isinstance(
            action,
            (
                CreateResourceOperationAction,
                ReadResourceOperationAction,
                UpdateResourceOperationAction,
                DeleteResourceOperationAction,
            ),
        ):
            raise ValueError(f"Invalid 'action' type: '{type(action)}'")

        if isinstance(action, CreateResourceOperationAction):
            return CreateFailedResourceOperationSchema(
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                resource=resource,
            )
        elif isinstance(action, ReadResourceOperationAction):
            return ReadFailedResourceOperationSchema(
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                resource=resource,
            )
        elif isinstance(action, UpdateResourceOperationAction):
            return UpdateFailedResourceOperationSchema(
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                resource=resource,
            )
        elif isinstance(action, DeleteResourceOperationAction):
            return DeleteFailedResourceOperationSchema(
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                resource=resource,
            )

    elif type is not None:
        if not isinstance(type, ResourceOperationType):
            raise ValueError(f"Unsupported `type`: {type}")

        if type is ResourceOperationType.CREATE:
            action = generate_resource_operation_action(
                type=type, create_type=create_type
            )
            return CreateFailedResourceOperationSchema(
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                resource=resource,
            )
        elif type is ResourceOperationType.READ:
            action = generate_resource_operation_action(type=type)
            return ReadFailedResourceOperationSchema(
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                resource=resource,
            )
        elif type is ResourceOperationType.UPDATE:
            action = generate_resource_operation_action(
                type=type,
                update_type=update_type,
                status_update_type=status_update_type,
            )
            return UpdateFailedResourceOperationSchema(
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                resource=resource,
            )
        elif type is ResourceOperationType.DELETE:
            action = generate_resource_operation_action(type=type)
            return DeleteFailedResourceOperationSchema(
                service_context=service_context,
                id=id,
                context=context,
                timestamp=timestamp,
                summary=summary,
                error=error,
                request_context=request_context,
                authentication=authentication,
                action=action,
                resource=resource,
            )
    else:
        # This should never happen due to your initial validation,
        # but type checker needs to see all paths covered
        raise ValueError("Neither 'action' nor 'type' provided")


class SuccessfulResourceOperationSchema(
    OperationResultMixin[ResourceOperationResultSchema[MetadataT]],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], ResourceOperationActionSchemaT],
    Generic[ResourceOperationActionSchemaT, MetadataT],
):
    success: Literal[True] = True


class NoDataResourceOperationSchema(
    OperationResultMixin[NoDataResourceOperationResult[MetadataT]],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], ResourceOperationActionSchemaT],
    Generic[ResourceOperationActionSchemaT, MetadataT],
):
    success: Literal[True] = True


class CreateSingleResourceOperationSchema(
    OperationResultMixin[CreateSingleResourceOperationResult[DataT, MetadataT]],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], CreateResourceOperationAction],
    Generic[DataT, MetadataT],
):
    success: Literal[True] = True


class ReadSingleResourceOperationSchema(
    OperationResultMixin[ReadSingleResourceOperationResult[DataT, MetadataT]],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], ReadResourceOperationAction],
    Generic[DataT, MetadataT],
):
    success: Literal[True] = True


class UpdateSingleResourceOperationSchema(
    OperationResultMixin[UpdateSingleResourceOperationResult[DataT, MetadataT]],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], UpdateResourceOperationAction],
    Generic[DataT, MetadataT],
):
    success: Literal[True] = True


class DeleteSingleResourceOperationSchema(
    OperationResultMixin[DeleteSingleResourceOperationResult[DataT, MetadataT]],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], DeleteResourceOperationAction],
    Generic[DataT, MetadataT],
):
    success: Literal[True] = True


class CreateMultipleResourceOperationSchema(
    OperationResultMixin[
        CreateMultipleResourceOperationResult[DataT, PaginationT, MetadataT]
    ],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], CreateResourceOperationAction],
    Generic[DataT, PaginationT, MetadataT],
):
    success: Literal[True] = True


class ReadMultipleResourceOperationSchema(
    OperationResultMixin[
        ReadMultipleResourceOperationResult[DataT, PaginationT, MetadataT]
    ],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], ReadResourceOperationAction],
    Generic[DataT, PaginationT, MetadataT],
):
    success: Literal[True] = True


class UpdateMultipleResourceOperationSchema(
    OperationResultMixin[
        UpdateMultipleResourceOperationResult[DataT, PaginationT, MetadataT]
    ],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], UpdateResourceOperationAction],
    Generic[DataT, PaginationT, MetadataT],
):
    success: Literal[True] = True


class DeleteMultipleResourceOperationSchema(
    OperationResultMixin[
        DeleteMultipleResourceOperationResult[DataT, PaginationT, MetadataT]
    ],
    NoErrorMixin,
    ResourceOperationSchema[Literal[True], DeleteResourceOperationAction],
    Generic[DataT, PaginationT, MetadataT],
):
    success: Literal[True] = True

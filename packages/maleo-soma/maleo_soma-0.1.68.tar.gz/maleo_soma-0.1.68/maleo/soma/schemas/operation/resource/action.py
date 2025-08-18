import re
from fastapi import Request
from pydantic import BaseModel, Field
from typing import Union, overload, Generic, Optional, TypeVar
from maleo.soma.enums.operation import (
    ResourceOperationType,
    ResourceOperationCreateType,
    ResourceOperationUpdateType,
    ResourceOperationDataUpdateType,
    ResourceOperationStatusUpdateType,
)
from maleo.soma.types.literals.operation import (
    ResourceOperationTypeLiteral,
    CreateResourceOperationTypeLiteral,
    ReadResourceOperationTypeLiteral,
    UpdateResourceOperationTypeLiteral,
    DeleteResourceOperationTypeLiteral,
)


class ResourceOperationActionSchema(BaseModel):
    type: ResourceOperationType = Field(..., description="Resource operation's type")
    create_type: Optional[ResourceOperationCreateType] = Field(
        None, description="Resource operation's create type (optional)"
    )
    update_type: Optional[ResourceOperationUpdateType] = Field(
        None, description="Resource operation's update type (optional)"
    )
    data_update_type: Optional[ResourceOperationDataUpdateType] = Field(
        None, description="Resource operation's data update type (optional)"
    )
    status_update_type: Optional[ResourceOperationStatusUpdateType] = Field(
        None, description="Resource operation's status update type (optional)"
    )


class CreateResourceOperationAction(ResourceOperationActionSchema):
    type: ResourceOperationType = ResourceOperationType.CREATE
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


class ReadResourceOperationAction(ResourceOperationActionSchema):
    type: ResourceOperationType = ResourceOperationType.READ
    create_type: Optional[ResourceOperationCreateType] = None
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


class UpdateResourceOperationAction(ResourceOperationActionSchema):
    type: ResourceOperationType = ResourceOperationType.UPDATE
    create_type: Optional[ResourceOperationCreateType] = None


class DeleteResourceOperationAction(ResourceOperationActionSchema):
    type: ResourceOperationType = ResourceOperationType.DELETE
    create_type: Optional[ResourceOperationCreateType] = None
    update_type: Optional[ResourceOperationUpdateType] = None
    data_update_type: Optional[ResourceOperationDataUpdateType] = None
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None


AllResourceOperationAction = Union[
    CreateResourceOperationAction,
    ReadResourceOperationAction,
    UpdateResourceOperationAction,
    DeleteResourceOperationAction,
]


def extract_resource_operation_action(
    request: Request, from_state: bool = True
) -> AllResourceOperationAction:
    if from_state:
        operation_action = request.state.resource_operation_action

        if not isinstance(
            operation_action,
            (
                CreateResourceOperationAction,
                ReadResourceOperationAction,
                UpdateResourceOperationAction,
                DeleteResourceOperationAction,
            ),
        ):
            raise TypeError(
                f"Invalid type of 'resource_operation_action': '{type(operation_action)}'"
            )

        return operation_action

    else:
        create_type = None
        update_type = None
        data_update_type = None
        status_update_type = None

        if request.method == "POST":
            if request.url.path.endswith("/restore"):
                create_type = ResourceOperationCreateType.RESTORE
            else:
                create_type = ResourceOperationCreateType.NEW
            return CreateResourceOperationAction(create_type=create_type)
        elif request.method == "GET":
            return ReadResourceOperationAction()
        elif request.method in ["PATCH", "PUT"]:
            if request.method == "PUT":
                update_type = ResourceOperationUpdateType.DATA
                data_update_type = ResourceOperationDataUpdateType.FULL
            elif request.method == "PATCH":
                if request.url.path.endswith("/status"):
                    update_type = ResourceOperationUpdateType.STATUS
                    if request.query_params is not None:
                        match = re.search(
                            r"[?&]action=([^&]+)",
                            (
                                ""
                                if not request.query_params
                                else str(request.query_params)
                            ),
                        )
                        if match:
                            try:
                                status_update_type = ResourceOperationStatusUpdateType(
                                    match.group(1)
                                )
                            except Exception:
                                pass
                else:
                    update_type = ResourceOperationUpdateType.DATA
                    data_update_type = ResourceOperationDataUpdateType.PARTIAL
            return UpdateResourceOperationAction(
                update_type=update_type,
                data_update_type=data_update_type,
                status_update_type=status_update_type,
            )
        elif request.method == "DELETE":
            return DeleteResourceOperationAction()
        else:
            raise ValueError("Unable to determine resource operation action")


def resource_operation_action_dependency(from_state: bool = True):

    def dependency(request: Request) -> AllResourceOperationAction:
        return extract_resource_operation_action(request, from_state=from_state)

    return dependency


ResourceOperationActionSchemaT = TypeVar(
    "ResourceOperationActionSchemaT", bound=ResourceOperationActionSchema
)


class ResourceOperationActionMixin(BaseModel, Generic[ResourceOperationActionSchemaT]):
    action: ResourceOperationActionSchemaT = Field(
        ..., description="Operation's action."
    )


@overload
def generate_resource_operation_action(
    *,
    type: CreateResourceOperationTypeLiteral,
    create_type: Optional[ResourceOperationCreateType] = ...,
) -> CreateResourceOperationAction: ...


@overload
def generate_resource_operation_action(
    *,
    type: ReadResourceOperationTypeLiteral,
) -> ReadResourceOperationAction: ...


@overload
def generate_resource_operation_action(
    *,
    type: UpdateResourceOperationTypeLiteral,
    update_type: Optional[ResourceOperationUpdateType] = ...,
    data_update_type: Optional[ResourceOperationDataUpdateType] = ...,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = ...,
) -> UpdateResourceOperationAction: ...


@overload
def generate_resource_operation_action(
    *,
    type: DeleteResourceOperationTypeLiteral,
) -> DeleteResourceOperationAction: ...


# Implementation
def generate_resource_operation_action(
    *,
    type: ResourceOperationTypeLiteral,
    create_type: Optional[ResourceOperationCreateType] = None,
    update_type: Optional[ResourceOperationUpdateType] = None,
    data_update_type: Optional[ResourceOperationDataUpdateType] = None,
    status_update_type: Optional[ResourceOperationStatusUpdateType] = None,
) -> AllResourceOperationAction:
    if not isinstance(type, ResourceOperationType):
        raise ValueError(f"Unsupported `type`: {type}")

    if type is ResourceOperationType.CREATE:
        return CreateResourceOperationAction(create_type=create_type)

    elif type is ResourceOperationType.READ:
        return ReadResourceOperationAction()

    elif type is ResourceOperationType.UPDATE:
        return UpdateResourceOperationAction(
            update_type=update_type,
            data_update_type=data_update_type,
            status_update_type=status_update_type,
        )

    elif type is ResourceOperationType.DELETE:
        return DeleteResourceOperationAction()


def from_request(
    request: Request, from_state: bool = True
) -> AllResourceOperationAction:
    if from_state:
        operation_action = request.state.operation_action

        if operation_action is None:
            raise ValueError(
                "Can not retrieve 'operation_action' from the current request state"
            )

        if not isinstance(
            operation_action,
            (
                CreateResourceOperationAction,
                ReadResourceOperationAction,
                UpdateResourceOperationAction,
                DeleteResourceOperationAction,
            ),
        ):
            raise ValueError(
                f"Invalid 'operation_action' type: '{type(operation_action)}'"
            )

        return operation_action

    if request.method == "POST":
        if request.url.path.endswith("/restore"):
            return generate_resource_operation_action(
                type=ResourceOperationType.CREATE,
                create_type=ResourceOperationCreateType.RESTORE,
            )
        else:
            return generate_resource_operation_action(
                type=ResourceOperationType.CREATE,
                create_type=ResourceOperationCreateType.NEW,
            )

    elif request.method == "GET":
        return generate_resource_operation_action(
            type=ResourceOperationType.READ,
        )

    elif request.method in ["PATCH", "PUT"]:
        if request.method == "PUT":
            return generate_resource_operation_action(
                type=ResourceOperationType.UPDATE,
                update_type=ResourceOperationUpdateType.DATA,
            )
        elif request.method == "PATCH":
            if not request.url.path.endswith("/status"):
                return generate_resource_operation_action(
                    type=ResourceOperationType.UPDATE,
                    update_type=ResourceOperationUpdateType.DATA,
                )
            else:
                if request.query_params is not None:
                    match = re.search(
                        r"[?&]action=([^&]+)",
                        ("" if not request.query_params else str(request.query_params)),
                    )
                    if match:
                        try:
                            return generate_resource_operation_action(
                                type=ResourceOperationType.UPDATE,
                                update_type=ResourceOperationUpdateType.STATUS,
                                status_update_type=ResourceOperationStatusUpdateType(
                                    match.group(1)
                                ),
                            )
                        except Exception:
                            return generate_resource_operation_action(
                                type=ResourceOperationType.UPDATE,
                                update_type=ResourceOperationUpdateType.STATUS,
                                status_update_type=None,
                            )

    elif request.method == "DELETE":
        return generate_resource_operation_action(
            type=ResourceOperationType.DELETE,
        )

    raise ValueError("Unable to map request's 'method' to 'operation_type'")

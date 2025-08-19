from typing import Literal, Optional
from maleo.soma.enums.operation import (
    ResourceOperationType,
    ResourceOperationCreateType,
    ResourceOperationUpdateType,
    ResourceOperationDataUpdateType,
    ResourceOperationStatusUpdateType,
)

# Operation type

CreateResourceOperationTypeLiteral = Literal[ResourceOperationType.CREATE]

OptionalCreateResourceOperationTypeLiteral = Optional[
    CreateResourceOperationTypeLiteral
]

ReadResourceOperationTypeLiteral = Literal[ResourceOperationType.READ]

OptionalReadResourceOperationTypeLiteral = Optional[ReadResourceOperationTypeLiteral]

UpdateResourceOperationTypeLiteral = Literal[ResourceOperationType.UPDATE]

OptionalUpdateResourceOperationTypeLiteral = Optional[
    UpdateResourceOperationTypeLiteral
]

DeleteResourceOperationTypeLiteral = Literal[ResourceOperationType.DELETE]

OptionalDeleteResourceOperationTypeLiteral = Optional[
    DeleteResourceOperationTypeLiteral
]

ResourceOperationTypeLiteral = Literal[
    ResourceOperationType.CREATE,
    ResourceOperationType.READ,
    ResourceOperationType.UPDATE,
    ResourceOperationType.DELETE,
]

OptionalResourceOperationTypeLiteral = Optional[ResourceOperationTypeLiteral]

# Operation create type

NewCreateResourceOperationCreateTypeLiteral = Literal[ResourceOperationCreateType.NEW]

OptionalNewCreateResourceOperationCreateTypeLiteral = Optional[
    NewCreateResourceOperationCreateTypeLiteral
]

RestoreCreateResourceOperationCreateTypeLiteral = Literal[
    ResourceOperationCreateType.RESTORE
]

OptionalRestoreCreateResourceOperationCreateTypeLiteral = Optional[
    RestoreCreateResourceOperationCreateTypeLiteral
]

ResourceOperationCreateTypeLiteral = Literal[
    ResourceOperationCreateType.NEW, ResourceOperationCreateType.RESTORE
]

OptionalResourceOperationCreateTypeLiteral = Optional[
    ResourceOperationCreateTypeLiteral
]

# Operation update type

DataUpdateResourceOperationUpdateTypeLiteral = Literal[ResourceOperationUpdateType.DATA]

OptionalDataUpdateResourceOperationUpdateTypeLiteral = Optional[
    DataUpdateResourceOperationUpdateTypeLiteral
]

StatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationUpdateType.STATUS
]

OptionalStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    StatusUpdateResourceOperationUpdateTypeLiteral
]

ResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationUpdateType.DATA,
    ResourceOperationUpdateType.STATUS,
]

OptionalResourceOperationUpdateTypeLiteral = Optional[
    ResourceOperationUpdateTypeLiteral
]

# Operation data update type

FullDataUpdateResourceOperationDataUpdateTypeLiteral = Literal[
    ResourceOperationDataUpdateType.FULL
]

OptionalFullDataUpdateResourceOperationDataUpdateTypeLiteral = Optional[
    FullDataUpdateResourceOperationDataUpdateTypeLiteral
]

PartialDataUpdateResourceOperationDataUpdateTypeLiteral = Literal[
    ResourceOperationDataUpdateType.PARTIAL
]

OptionalPartialDataUpdateResourceOperationDataUpdateTypeLiteral = Optional[
    PartialDataUpdateResourceOperationDataUpdateTypeLiteral
]

ResourceOperationDataUpdateTypeLiteral = Literal[
    ResourceOperationDataUpdateType.FULL,
    ResourceOperationDataUpdateType.PARTIAL,
]

OptionalResourceOperationDataUpdateTypeLiteral = Optional[
    ResourceOperationDataUpdateTypeLiteral
]

# Operation status update type

ActivateStatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.ACTIVATE
]

OptionalActivateStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    ActivateStatusUpdateResourceOperationUpdateTypeLiteral
]

DeactivateStatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.DEACTIVATE
]

OptionalDeactivateStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    DeactivateStatusUpdateResourceOperationUpdateTypeLiteral
]

RestoreStatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.RESTORE
]

OptionalRestoreStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    RestoreStatusUpdateResourceOperationUpdateTypeLiteral
]

DeleteStatusUpdateResourceOperationUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.DELETE
]

OptionalDeleteStatusUpdateResourceOperationUpdateTypeLiteral = Optional[
    DeleteStatusUpdateResourceOperationUpdateTypeLiteral
]

ResourceOperationStatusUpdateTypeLiteral = Literal[
    ResourceOperationStatusUpdateType.ACTIVATE,
    ResourceOperationStatusUpdateType.DEACTIVATE,
    ResourceOperationStatusUpdateType.RESTORE,
    ResourceOperationStatusUpdateType.DELETE,
]

OptionalResourceOperationStatusUpdateTypeLiteral = Optional[
    ResourceOperationStatusUpdateTypeLiteral
]

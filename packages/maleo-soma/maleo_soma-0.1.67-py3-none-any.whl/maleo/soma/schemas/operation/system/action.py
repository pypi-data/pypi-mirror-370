from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.enums.operation import SystemOperationType
from maleo.soma.types.base import OptionalStringToAnyDict


class SystemOperationActionSchema(BaseModel):
    type: SystemOperationType = Field(..., description="Action's type")
    details: OptionalStringToAnyDict = Field(None, description="Action's details")


class SystemOperationActionMixin(SystemOperationActionSchema):
    action: SystemOperationActionSchema = Field(..., description="Operation's action")


class OptionalSystemOperationActionMixin(SystemOperationActionSchema):
    action: Optional[SystemOperationActionSchema] = Field(
        None, description="Operation's action. (Optional)"
    )

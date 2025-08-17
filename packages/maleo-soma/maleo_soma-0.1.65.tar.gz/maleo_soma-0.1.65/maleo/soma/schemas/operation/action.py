from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar


OperationActionSchemaT = TypeVar("OperationActionSchemaT", bound=BaseModel)


class OperationActionMixin(BaseModel, Generic[OperationActionSchemaT]):
    action: OperationActionSchemaT = Field(..., description="Action.")


class OptionalOperationActionMixin(BaseModel, Generic[OperationActionSchemaT]):
    action: Optional[OperationActionSchemaT] = Field(
        None, description="Action. (Optional)"
    )

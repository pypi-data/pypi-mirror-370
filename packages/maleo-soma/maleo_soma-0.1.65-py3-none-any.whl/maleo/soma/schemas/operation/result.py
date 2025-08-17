from pydantic import BaseModel, Field
from typing import Any, Generic, Optional, TypeVar


class AnyOperationResultMixin(BaseModel):
    result: Any = Field(..., description="Result.")


class NoOperationResultMixin(AnyOperationResultMixin):
    result: None = None


OperationResultSchemaT = TypeVar("OperationResultSchemaT")


class OperationResultMixin(AnyOperationResultMixin, Generic[OperationResultSchemaT]):
    result: OperationResultSchemaT = Field(..., description="Result.")


class OptionalOperationResultMixin(
    AnyOperationResultMixin, Generic[OperationResultSchemaT]
):
    result: Optional[OperationResultSchemaT] = Field(
        None, description="Result. (Optional)"
    )

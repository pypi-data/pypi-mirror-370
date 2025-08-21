from pydantic import BaseModel, Field
from typing import Any, Generic, List, Optional, TypeVar


# ! Do not instantiate and use this class
# * This class is created for future type override
class AnyDataMixin(BaseModel):
    data: Any = Field(..., description="Any Data.")


class NoDataMixin(AnyDataMixin):
    data: None = None


DataT = TypeVar("DataT")


class DataMixin(AnyDataMixin, Generic[DataT]):
    data: DataT = Field(..., description="Data.")


class SingleDataMixin(DataMixin[DataT], Generic[DataT]):
    pass


class OptionalSingleDataMixin(DataMixin[Optional[DataT]], Generic[DataT]):
    pass


class MultipleDataMixin(DataMixin[List[DataT]], Generic[DataT]):
    pass


class OptionalMultipleDataMixin(DataMixin[Optional[List[DataT]]], Generic[DataT]):
    pass


OldDataT = TypeVar("OldDataT")
NewDataT = TypeVar("NewDataT")


class DataPair(BaseModel, Generic[OldDataT, NewDataT]):
    old: OldDataT = Field(..., description="Old data")
    new: NewDataT = Field(..., description="New data")


class NoDataPair(DataPair[None, None]):
    old: None = None
    new: None = None

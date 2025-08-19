from pydantic import BaseModel, Field
from typing import Generic, List
from maleo.soma.mixins.general import OptionalOther
from maleo.soma.schemas.data import (
    AnyDataMixin,
    NoDataMixin,
    DataT,
    DataMixin,
    DataPair,
)
from maleo.soma.schemas.result.descriptor import (
    AnyDataResultDescriptorSchema,
    NoDataResultDescriptorSchema,
    CreateSingleDataResultDescriptorSchema,
    ReadSingleDataResultDescriptorSchema,
    UpdateSingleDataResultDescriptorSchema,
    DeleteSingleDataResultDescriptorSchema,
    CreateMultipleDataResultDescriptorSchema,
    ReadMultipleDataResultDescriptorSchema,
    UpdateMultipleDataResultDescriptorSchema,
    DeleteMultipleDataResultDescriptorSchema,
)
from maleo.soma.schemas.metadata import OptionalMetadataMixin, MetadataT
from maleo.soma.schemas.pagination import (
    AnyPaginationMixin,
    NoPaginationMixin,
    PaginationT,
    PaginationMixin,
)


class ResourceOperationResultSchema(
    OptionalOther,
    OptionalMetadataMixin[MetadataT],
    AnyPaginationMixin,
    AnyDataMixin,
    AnyDataResultDescriptorSchema,
    BaseModel,
    Generic[MetadataT],
):
    pass


class NoDataResourceOperationResult(
    NoPaginationMixin,
    NoDataMixin,
    NoDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[MetadataT],
):
    pass


class NoDataResourceOperationResultMixin(Generic[MetadataT]):
    result: NoDataResourceOperationResult[MetadataT] = Field(..., description="Result")


class CreateSingleResourceOperationResult(
    NoPaginationMixin,
    DataMixin[DataPair[None, DataT]],
    CreateSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class CreateSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: CreateSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class ReadSingleResourceOperationResult(
    NoPaginationMixin,
    DataMixin[DataPair[DataT, None]],
    ReadSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class ReadSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: ReadSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class UpdateSingleResourceOperationResult(
    NoPaginationMixin,
    DataMixin[DataPair[DataT, DataT]],
    UpdateSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class UpdateSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: UpdateSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class DeleteSingleResourceOperationResult(
    NoPaginationMixin,
    DataMixin[DataPair[DataT, None]],
    DeleteSingleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class DeleteSingleResourceOperationResultMixin(Generic[DataT, MetadataT]):
    result: DeleteSingleResourceOperationResult[DataT, MetadataT] = Field(
        ..., description="Result"
    )


class CreateMultipleResourceOperationResult(
    PaginationMixin[PaginationT],
    DataMixin[DataPair[None, List[DataT]]],
    CreateMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class CreateMultipleResourceOperationResultMixin(
    Generic[DataT, PaginationT, MetadataT]
):
    result: CreateMultipleResourceOperationResult[DataT, PaginationT, MetadataT] = (
        Field(..., description="Result")
    )


class ReadMultipleResourceOperationResult(
    PaginationMixin[PaginationT],
    DataMixin[DataPair[List[DataT], None]],
    ReadMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class ReadMultipleResourceOperationResultMixin(Generic[DataT, PaginationT, MetadataT]):
    result: ReadMultipleResourceOperationResult[DataT, PaginationT, MetadataT] = Field(
        ..., description="Result"
    )


class UpdateMultipleResourceOperationResult(
    PaginationMixin[PaginationT],
    DataMixin[DataPair[List[DataT], List[DataT]]],
    UpdateMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class UpdateMultipleResourceOperationResultMixin(
    Generic[DataT, PaginationT, MetadataT]
):
    result: UpdateMultipleResourceOperationResult[DataT, PaginationT, MetadataT] = (
        Field(..., description="Result")
    )


class DeleteMultipleResourceOperationResult(
    PaginationMixin[PaginationT],
    DataMixin[DataPair[List[DataT], None]],
    DeleteMultipleDataResultDescriptorSchema,
    ResourceOperationResultSchema[MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class DeleteMultipleResourceOperationResultMixin(
    Generic[DataT, PaginationT, MetadataT]
):
    result: DeleteMultipleResourceOperationResult[DataT, PaginationT, MetadataT] = (
        Field(..., description="Result")
    )

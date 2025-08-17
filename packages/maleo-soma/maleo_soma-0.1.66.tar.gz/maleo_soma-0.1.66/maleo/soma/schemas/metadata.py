from pydantic import BaseModel, Field
from typing import Any, Dict, Generic, Optional, TypeVar, Union
from maleo.soma.mixins.general import Success, Code, Message, Description, OptionalOther


class AnyMetadataMixin(BaseModel):
    metadata: Any = Field(..., description="Metadata")


class NoMetadataMixin(AnyMetadataMixin):
    metadata: None = None


MetadataT = TypeVar("MetadataT")


class MetadataMixin(BaseModel, Generic[MetadataT]):
    metadata: MetadataT = Field(..., description="Metadata")


class OptionalMetadataMixin(BaseModel, Generic[MetadataT]):
    metadata: Optional[MetadataT] = Field(..., description="Metadata. (Optional)")


class FieldExpansionMetadata(OptionalOther, Description, Message, Code[str], Success):
    pass


class FieldExpansionMetadataMixin(BaseModel):
    field_expansion: Optional[Union[str, Dict[str, FieldExpansionMetadata]]] = Field(
        None, description="Field expansion metadata"
    )

from typing import List, Optional
from pydantic import BaseModel, Field
from maleo.soma.types.base import OptionalStringToAnyDict
from .identifier import ResourceIdentifier


class Resource(BaseModel):
    identifiers: List[ResourceIdentifier] = Field(
        ..., min_length=1, description="Identifiers"
    )
    details: OptionalStringToAnyDict = Field(None, description="Details")

    def aggregate(self, sep: str = ":") -> str:
        return sep.join([id.key for id in self.identifiers])


class ResourceMixin(BaseModel):
    resource: Resource = Field(..., description="Resource")


class OptionalResourceMixin(BaseModel):
    resource: Optional[Resource] = Field(None, description="Resource. (Optional)")

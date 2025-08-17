from pydantic import BaseModel, Field
from maleo.soma.types.base import OptionalAny, OptionalListOfStrings


class ErrorMetadataSchema(BaseModel):
    details: OptionalAny = Field(None, description="Details")
    traceback: OptionalListOfStrings = Field(None, description="Traceback")

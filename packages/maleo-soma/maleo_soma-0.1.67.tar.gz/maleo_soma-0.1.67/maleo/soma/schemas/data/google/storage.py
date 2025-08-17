from pydantic import BaseModel, Field


class StorageDataSchema(BaseModel):
    url: str = Field(..., description="File's URL")

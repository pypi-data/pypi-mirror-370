from pydantic import BaseModel, Field
from maleo.soma.enums.service import Service


class ServiceConfigurationDTO(BaseModel):
    key: Service = Field(..., description="Service's key")
    name: str = Field(..., description="Service's name")
    host: str = Field(..., description="Service's host")
    port: int = Field(..., description="Service's port")

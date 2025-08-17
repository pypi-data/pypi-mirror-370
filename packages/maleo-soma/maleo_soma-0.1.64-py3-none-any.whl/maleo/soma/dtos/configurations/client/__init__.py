from pydantic import BaseModel, Field
from .maleo import MaleoClientsConfigurationDTO


class ClientConfigurationDTO(BaseModel):
    maleo: MaleoClientsConfigurationDTO = Field(
        default=...,
        description="Maleo client's configurations",
    )

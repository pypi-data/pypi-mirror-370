from pydantic import BaseModel, Field
from typing import Generic
from .maleo import MaleoClientsConfigurationT


class ClientConfigurationDTO(BaseModel, Generic[MaleoClientsConfigurationT]):
    maleo: MaleoClientsConfigurationT = Field(
        default=...,
        description="Maleo client's configurations",
    )

from pydantic import BaseModel, Field
from typing import Generic, Optional
from .maleo import MaleoClientsConfigurationT


class ClientConfigurationDTO(BaseModel, Generic[MaleoClientsConfigurationT]):
    maleo: Optional[MaleoClientsConfigurationT] = Field(
        None,
        description="Maleo client's configurations",
    )

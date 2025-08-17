from pydantic import BaseModel, Field
from maleo.soma.types.base import OptionalSequenceOfStrings
from .publisher import PublisherConfigurationDTO


class PubSubConfigurationDTO(BaseModel):
    publisher: PublisherConfigurationDTO = Field(
        default_factory=PublisherConfigurationDTO,
        description="Publisher's configurations",
    )
    subscriptions: OptionalSequenceOfStrings = Field(None, description="Subscriptions")

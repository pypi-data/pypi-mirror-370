from pydantic import BaseModel, Field
from typing import Generic
from .publisher import AdditionalTopicsConfigurationT, PublisherConfigurationDTO
from .subscription import SubscriptionsConfigurationT


class PubSubConfigurationDTO(
    BaseModel, Generic[SubscriptionsConfigurationT, AdditionalTopicsConfigurationT]
):
    publisher: PublisherConfigurationDTO[AdditionalTopicsConfigurationT] = Field(
        ...,
        description="Publisher's configurations",
    )
    subscriptions: SubscriptionsConfigurationT = Field(..., description="Subscriptions")

from pydantic import BaseModel, ConfigDict, Field
from typing import Generic, TypeVar
from maleo.soma.utils.logging import (
    ApplicationLogger,
    CacheLogger,
    ControllerLogger,
    DatabaseLogger,
    MiddlewareLogger,
    RepositoryLogger,
    ServiceLogger,
)
from .cache import CacheConfigurationDTO
from .client import ClientConfigurationDTO
from .client.maleo import MaleoClientsConfigurationT
from .database import DatabaseConfigurationDTO
from .middleware import MiddlewareConfigurationDTO
from .pubsub import PubSubConfigurationDTO
from .pubsub.publisher import AdditionalTopicsConfigurationT
from .pubsub.subscription import SubscriptionsConfigurationT
from .service import ServiceConfigurationDTO


class ConfigurationDTO(
    BaseModel,
    Generic[
        SubscriptionsConfigurationT,
        AdditionalTopicsConfigurationT,
        MaleoClientsConfigurationT,
    ],
):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cache: CacheConfigurationDTO = Field(..., description="Cache's configurations")
    client: ClientConfigurationDTO[MaleoClientsConfigurationT] = Field(
        ..., description="Client's configurations"
    )
    database: DatabaseConfigurationDTO = Field(
        ..., description="Database's configurations"
    )
    middleware: MiddlewareConfigurationDTO = Field(
        ..., description="Middleware's configurations"
    )
    pubsub: PubSubConfigurationDTO[
        SubscriptionsConfigurationT,
        AdditionalTopicsConfigurationT,
    ] = Field(..., description="PubSub's configurations")
    service: ServiceConfigurationDTO = Field(
        ..., description="Service's configurations"
    )


ConfigurationT = TypeVar("ConfigurationT", bound=ConfigurationDTO)


class LoggerDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    application: ApplicationLogger = Field(..., description="Application logger")
    cache: CacheLogger = Field(..., description="Cache logger")
    controller: ControllerLogger = Field(..., description="Controller logger")
    database: DatabaseLogger = Field(..., description="Database logger")
    middleware: MiddlewareLogger = Field(..., description="Middleware logger")
    repository: RepositoryLogger = Field(..., description="Repository logger")
    service: ServiceLogger = Field(..., description="Service logger")

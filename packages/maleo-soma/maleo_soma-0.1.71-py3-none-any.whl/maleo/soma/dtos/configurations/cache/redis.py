from pydantic import BaseModel, Field
from typing import Union
from maleo.soma.enums.cache import CacheLayer, CacheOrigin
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.expiration import Expiration
from maleo.soma.types.base import OptionalString


class RedisCacheNamespaces(BaseModel):
    base: str = Field(..., description="Base's redis namespace")

    def create(
        self,
        *ext: str,
        origin: CacheOrigin,
        layer: CacheLayer,
        base_override: OptionalString = None,
    ) -> str:
        return ":".join(
            [self.base if base_override is None else base_override, origin, layer, *ext]
        )


class RedisCacheConfigurationDTO(BaseModel):
    environment: Environment = Field(..., description="Redis cache's environment")
    ttl: Union[int, float] = Field(Expiration.EXP_5MN.value, description="Default TTL")
    namespaces: RedisCacheNamespaces = Field(
        ..., description="Redis cache's namepsaces"
    )
    host: str = Field(..., description="Redis instance's host")
    port: int = Field(6379, description="Redis instance's port")
    db: int = Field(0, description="Redis instance's db")
    password: OptionalString = Field(None, description="AUTH password")
    decode_responses: bool = Field(True, description="Whether to decode responses")
    health_check_interval: int = Field(30, description="Health check interval")

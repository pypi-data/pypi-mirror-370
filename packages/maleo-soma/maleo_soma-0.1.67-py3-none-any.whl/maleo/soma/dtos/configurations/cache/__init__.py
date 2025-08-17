from __future__ import annotations
from pydantic import BaseModel, Field
from .redis import RedisCacheConfigurationDTO


class CacheConfigurationDTO(BaseModel):
    redis: RedisCacheConfigurationDTO = Field(
        ..., description="Redis cache's configurations"
    )

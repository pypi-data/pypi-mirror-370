import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.service import Service


class ServiceContext(BaseModel):
    environment: Environment = Field(..., description="Service's environment")
    key: Service = Field(..., description="Service's key")

    @classmethod
    def from_env(cls) -> "ServiceContext":
        load_dotenv()
        environment = os.getenv("ENVIRONMENT", None)
        if environment is None:
            raise ValueError("Variable 'ENVIRONMENT' not found in ENV")

        key = os.getenv("SERVICE_KEY", None)
        if key is None:
            raise ValueError("Variable 'SERVICE_KEY' not found in ENV")

        return cls(environment=Environment(environment), key=Service(key))


class ServiceContextMixin(BaseModel):
    service_context: ServiceContext = Field(..., description="Service's context")


class OptionalServiceContextMixin(BaseModel):
    service_context: Optional[ServiceContext] = Field(
        None, description="Service's context. (Optional)"
    )

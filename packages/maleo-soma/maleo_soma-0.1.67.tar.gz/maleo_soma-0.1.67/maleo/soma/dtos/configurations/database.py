from pydantic import BaseModel, Field
from maleo.soma.enums.environment import Environment


class DatabaseConfigurationDTO(BaseModel):
    environment: Environment = Field(..., description="Database's environment")
    username: str = Field("postgres", description="Database user's username")
    password: str = Field(..., description="Database user's password")
    host: str = Field(..., description="Database's host")
    port: int = Field(5432, description="Database's port")
    database: str = Field(..., description="Database's name")

    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

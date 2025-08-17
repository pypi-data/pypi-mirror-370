from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from maleo.soma.constants import TOKEN_SCHEME


class Authorization(BaseModel):
    scheme: str = Field(..., description="Authorization's scheme")
    credentials: str = Field(..., description="Authorization's credentials")

    @classmethod
    def from_request(cls, token: HTTPAuthorizationCredentials = Security(TOKEN_SCHEME)):
        return cls(scheme=token.scheme, credentials=token.credentials)


class AuthorizationMixin(BaseModel):
    authorization: Authorization = Field(
        ...,
        description="Authorization",
    )


class OptionalAuthorizationMixin(BaseModel):
    authorization: Optional[Authorization] = Field(
        None,
        description="Authorization. (Optional)",
    )

from fastapi import Request
from pydantic import BaseModel, Field
from typing import Optional, Sequence
from maleo.soma.authentication import (
    Credentials as RequestCredentials,
    User as RequestUser,
)
from maleo.soma.schemas.token import AuthenticationToken


class Credentials(BaseModel):
    token: Optional[AuthenticationToken] = Field(None, description="Token")
    scopes: Optional[Sequence[str]] = Field(None, description="Scopes")


class User(BaseModel):
    is_authenticated: bool = Field(False, description="Authenticated")
    display_name: str = Field("", description="Username")
    identity: str = Field("", description="Email")


class Authentication(BaseModel):
    credentials: Credentials = Field(
        default_factory=Credentials,  # type: ignore
        description="Credential",
    )
    user: User = Field(
        default_factory=User,  # type: ignore
        description="User",
    )

    @classmethod
    def from_request(
        cls, request: Request, from_state: bool = True
    ) -> "Authentication":
        if from_state:
            if not hasattr(request.state, "authentication"):
                raise AttributeError(
                    "Request state dit not have 'authentication' attribute"
                )
            if not isinstance(request.state.authentication, cls):
                raise TypeError(
                    f"Invalid type of 'authentication' attribute: '{type(request.state.authentication)}'"
                )
            return request.state.authentication

        else:
            # validate credentials
            request_credentials = request.auth
            if not isinstance(request_credentials, RequestCredentials):
                raise TypeError("'credentials' is not of type 'RequestCredentials'")
            credentials = Credentials.model_validate(
                request_credentials, from_attributes=True
            )
            # validate user
            request_user = request.user
            if not isinstance(request_user, RequestUser):
                raise TypeError("'user' is not of type 'RequestUser'")
            user = User.model_validate(request_user, from_attributes=True)
            return cls(credentials=credentials, user=user)

    @classmethod
    def as_dependency(cls, from_state: bool = True):
        """Create a FastAPI dependency for this authentication."""

        def dependency(request: Request) -> "Authentication":
            return cls.from_request(request, from_state=from_state)

        return dependency


class AuthenticationMixin(BaseModel):
    authentication: Authentication = Field(
        ...,
        description="Authentication",
    )


class OptionalAuthenticationMixin(BaseModel):
    authentication: Optional[Authentication] = Field(
        None,
        description="Authentication. (Optional)",
    )

from Crypto.PublicKey.RSA import RsaKey
from fastapi import FastAPI
from starlette.authentication import AuthenticationBackend, AuthenticationError
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from typing import Tuple
from maleo.soma.authentication import Credentials, User
from maleo.soma.enums.token import TokenType
from maleo.soma.schemas.token import AuthenticationToken
from maleo.soma.utils.exceptions.request import authentication_error_handler
from maleo.soma.utils.token import decode


class Backend(AuthenticationBackend):
    def __init__(
        self,
        public_key: RsaKey,
    ):
        super().__init__()
        self._public_key = public_key

    async def authenticate(self, conn: HTTPConnection) -> Tuple[Credentials, User]:
        if "Authorization" in conn.headers:
            auth = conn.headers["Authorization"]
            parts = auth.split()
            if len(parts) != 2 or parts[0] != "Bearer":
                raise AuthenticationError("Invalid Authorization header format")
            scheme, token = parts
            if scheme != "Bearer":
                raise AuthenticationError("Authorization scheme must be Bearer token")

            # Decode token
            try:
                payload = decode(token=token, key=self._public_key)
            except Exception as e:
                raise AuthenticationError(str(e))
            type = TokenType.ACCESS
            token = AuthenticationToken(type=type, payload=payload)
            return (
                Credentials(token=token, scopes=["authenticated", payload.sr]),
                User(authenticated=True, username=payload.u_u, email=payload.u_e),
            )

        if "token" in conn.cookies:
            token = conn.cookies["token"]
            # Decode token
            try:
                payload = decode(token=token, key=self._public_key)
            except Exception as e:
                raise AuthenticationError(str(e))
            type = TokenType.REFRESH
            token = AuthenticationToken(type=type, payload=payload)
            return (
                Credentials(token=token, scopes=["authenticated", payload.sr]),
                User(authenticated=True, username=payload.u_u, email=payload.u_e),
            )

        return Credentials(), User()


def add_authentication_middleware(
    app: FastAPI,
    *,
    public_key: RsaKey,
) -> None:
    """
    Adds Authentication middleware to the FastAPI application.

    Args:
        app: FastAPI
            The FastAPI application instance to which the middleware will be added.

        key: str
            Public key to be used for token decoding.

    Returns:
        None: The function modifies the FastAPI app by adding Base middleware.

    Note:
        FastAPI applies middleware in reverse order of registration, so this middleware
        will execute after any middleware added subsequently.

    Example:
    ```python
    add_authentication_middleware(app=app, limit=10, window=1, cleanup_interval=60, ip_timeout=300)
    ```
    """
    app.add_middleware(
        AuthenticationMiddleware,
        backend=Backend(public_key),
        on_error=authentication_error_handler,  # type: ignore
    )

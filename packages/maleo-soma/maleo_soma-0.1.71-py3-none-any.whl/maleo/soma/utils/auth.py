from Crypto.PublicKey.RSA import RsaKey
from typing import Optional
from maleo.soma.schemas.authentication import Authentication
from maleo.soma.schemas.authorization import Authorization
from .token import reencode


def validate_authentication_authorization(
    private_key: RsaKey,
    authentication: Authentication,
    authorization: Optional[Authorization] = None,
):
    if (
        authentication.credentials.token is not None
        and authorization is not None
        and authorization.scheme == "bearer"
    ):
        authentication_token = reencode(
            authentication.credentials.token.payload, key=private_key
        )
        authorization_token = authorization.credentials
        if authentication_token != authorization_token:
            raise ValueError(
                "Token from authentication did not matched with authorization"
            )

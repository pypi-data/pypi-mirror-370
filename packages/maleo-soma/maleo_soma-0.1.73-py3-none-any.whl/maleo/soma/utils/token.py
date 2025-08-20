import jwt
from collections.abc import Iterable, Sequence
from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timedelta, timezone
from typing import Union, overload
from maleo.soma.enums.expiration import Expiration
from maleo.soma.enums.key import RSAKeyType
from maleo.soma.schemas.token import CredentialPayload, TimestampPayload, Payload
from maleo.soma.types.base import BytesOrString, OptionalDatetime, OptionalString
from maleo.soma.utils.loaders.key.rsa import with_pycryptodome


@overload
def reencode(
    payload: Payload,
    key: RsaKey,
) -> str: ...
@overload
def reencode(
    payload: Payload,
    key: BytesOrString,
    *,
    password: OptionalString = None,
) -> str: ...
def reencode(
    payload: Payload,
    key: Union[RsaKey, BytesOrString],
    *,
    password: OptionalString = None,
) -> str:
    if isinstance(key, RsaKey):
        private_key = key
    else:
        private_key = with_pycryptodome(
            RSAKeyType.PRIVATE, extern_key=key, passphrase=password
        )

    token = jwt.encode(
        payload=payload.model_dump(mode="json"),
        key=private_key.export_key(),
        algorithm="RS256",
    )

    return token


@overload
def encode(
    credential: CredentialPayload,
    key: RsaKey,
    *,
    iat_dt: OptionalDatetime = None,
    exp_in: Expiration = Expiration.EXP_15MN,
) -> str: ...
@overload
def encode(
    credential: CredentialPayload,
    key: BytesOrString,
    *,
    password: OptionalString = None,
    iat_dt: OptionalDatetime = None,
    exp_in: Expiration = Expiration.EXP_15MN,
) -> str: ...
def encode(
    credential: CredentialPayload,
    key: Union[RsaKey, BytesOrString],
    *,
    password: OptionalString = None,
    iat_dt: OptionalDatetime = None,
    exp_in: Expiration = Expiration.EXP_15MN,
) -> str:
    if iat_dt is None:
        iat_dt = datetime.now(tz=timezone.utc)
    iat = int(iat_dt.timestamp())
    exp_dt = iat_dt + timedelta(seconds=exp_in.value)
    exp = int(exp_dt.timestamp())

    timestamp = TimestampPayload(iat_dt=iat_dt, iat=iat, exp_dt=exp_dt, exp=exp)

    payload = Payload.model_validate(
        {**credential.model_dump(), **timestamp.model_dump()}
    )

    if isinstance(key, RsaKey):
        private_key = key
    else:
        private_key = with_pycryptodome(
            RSAKeyType.PRIVATE, extern_key=key, passphrase=password
        )

    token = jwt.encode(
        payload=payload.model_dump(mode="json"),
        key=private_key.export_key(),
        algorithm="RS256",
    )

    return token


def decode(
    token: str,
    key: Union[RsaKey, BytesOrString],
    audience: str | Iterable[str] | None = None,
    subject: str | None = None,
    issuer: str | Sequence[str] | None = None,
    leeway: float | timedelta = 0,
) -> Payload:
    payload_dict = jwt.decode(
        jwt=token,
        key=key.export_key() if isinstance(key, RsaKey) else key,
        algorithms=["RS256"],
        audience=audience,
        subject=subject,
        issuer=issuer,
        leeway=leeway,
    )

    payload = Payload.model_validate(payload_dict)

    return payload

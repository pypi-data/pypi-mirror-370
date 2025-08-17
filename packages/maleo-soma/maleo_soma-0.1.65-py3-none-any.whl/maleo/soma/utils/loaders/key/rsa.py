from cryptography.hazmat.primitives import serialization
from Crypto.PublicKey import RSA
from pathlib import Path
from typing import overload, Optional, Union
from maleo.soma.enums.key import KeyFormat, RSAKeyType
from maleo.soma.types.base import (
    BytesOrString,
    OptionalBytesOrString,
    OptionalBytes,
    OptionalString,
)
from maleo.soma.types.literals.key import (
    BytesKeyFormatLiteral,
    StringKeyFormatLiteral,
    PrivateRSAKeyTypeLiteral,
    PublicRSAKeyTypeLiteral,
)


def with_pycryptodome(
    type: RSAKeyType,
    *,
    extern_key: BytesOrString,
    passphrase: OptionalString = None,
) -> RSA.RsaKey:
    if not isinstance(type, RSAKeyType):
        raise TypeError("Invalid key type")

    if not isinstance(extern_key, (str, bytes)):
        raise TypeError("Invalid external key type")

    if type == RSAKeyType.PRIVATE:
        private_key = RSA.import_key(extern_key=extern_key, passphrase=passphrase)
        if not private_key.has_private():
            raise TypeError(
                "Invalid chosen key type, the private key did not have private inside it"
            )
        return private_key

    if type == RSAKeyType.PUBLIC:
        public_key = RSA.import_key(extern_key=extern_key)
        if public_key.has_private():
            raise TypeError(
                "Invalid chosen key type, the public key had private inside it"
            )
        return public_key


@overload
def with_cryptography(
    format: BytesKeyFormatLiteral,
    type: PrivateRSAKeyTypeLiteral,
    *,
    data: OptionalBytes = None,
    path: Optional[Union[str, Path]] = None,
    password: OptionalBytes = None,
) -> bytes: ...
@overload
def with_cryptography(
    format: StringKeyFormatLiteral,
    type: PrivateRSAKeyTypeLiteral,
    *,
    data: OptionalString = None,
    path: Optional[Union[str, Path]] = None,
    password: OptionalString = None,
) -> str: ...
@overload
def with_cryptography(
    format: BytesKeyFormatLiteral,
    type: PublicRSAKeyTypeLiteral,
    *,
    data: OptionalBytes = None,
    path: Optional[Union[str, Path]] = None,
) -> bytes: ...
@overload
def with_cryptography(
    format: StringKeyFormatLiteral,
    type: PublicRSAKeyTypeLiteral,
    *,
    data: OptionalString = None,
    path: Optional[Union[str, Path]] = None,
) -> str: ...
def with_cryptography(
    format: KeyFormat,
    type: RSAKeyType,
    *,
    data: OptionalBytesOrString = None,
    path: Optional[Union[str, Path]] = None,
    password: OptionalBytesOrString = None,
) -> BytesOrString:
    if not isinstance(type, RSAKeyType):
        raise TypeError("Invalid key type")

    if data is None and path is None:
        raise ValueError("Either data or path must be provided")

    if data is not None and path is not None:
        raise ValueError("Only either data or path will be accepted as parameters")

    key_data: Optional[bytes] = None

    if data is not None:
        if isinstance(data, bytes):
            key_data = data
        elif isinstance(data, str):
            key_data = data.encode()
        else:
            raise TypeError("Invalid data type")

    if path is not None:
        file_path = Path(path)

        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Key file not found: {file_path}")

        key_data = file_path.read_bytes()

    if key_data is None:
        raise ValueError("Key data is required")

    if password is not None and not isinstance(password, (str, bytes)):
        raise TypeError("Invalid passsword type")

    if not isinstance(format, KeyFormat):
        raise TypeError("Invalid key format type")

    if type == RSAKeyType.PRIVATE:
        private_key = serialization.load_pem_private_key(
            key_data,
            password=password.encode() if isinstance(password, str) else password,
        )
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        if format == KeyFormat.BYTES:
            return private_key_bytes
        elif format == KeyFormat.STRING:
            return private_key_bytes.decode()

    if type == RSAKeyType.PUBLIC:
        public_key = serialization.load_pem_public_key(key_data)
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        if format == KeyFormat.BYTES:
            return public_key_bytes
        elif format == KeyFormat.STRING:
            return public_key_bytes.decode()

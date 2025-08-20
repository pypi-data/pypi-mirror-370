from typing import Literal, Optional
from maleo.soma.enums.key import KeyFormat, RSAKeyType

BytesKeyFormatLiteral = Literal[KeyFormat.BYTES]

OptionalBytesKeyFormatLiteral = Optional[BytesKeyFormatLiteral]

StringKeyFormatLiteral = Literal[KeyFormat.STRING]

OptionalStringKeyFormatLiteral = Optional[StringKeyFormatLiteral]

KeyFormatLiteral = Literal[KeyFormat.BYTES, KeyFormat.STRING]

OptionalKeyFormatLiteral = Optional[KeyFormatLiteral]

PrivateRSAKeyTypeLiteral = Literal[RSAKeyType.PRIVATE]

OptionalPrivateRSAKeyTypeLiteral = Optional[PrivateRSAKeyTypeLiteral]

PublicRSAKeyTypeLiteral = Literal[RSAKeyType.PUBLIC]

OptionalPublicRSAKeyTypeLiteral = Optional[PublicRSAKeyTypeLiteral]

RSAKeyTypeLiteral = Literal[RSAKeyType.PRIVATE, RSAKeyType.PUBLIC]

OptionalRSAKeyTypeLiteral = Optional[RSAKeyTypeLiteral]

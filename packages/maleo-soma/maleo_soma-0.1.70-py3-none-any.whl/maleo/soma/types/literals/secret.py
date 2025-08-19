from typing import Literal, Optional
from maleo.soma.enums.secret import SecretFormat

BytesSecretFormatLiteral = Literal[SecretFormat.BYTES]

OptionalBytesSecretFormatLiteral = Optional[BytesSecretFormatLiteral]

StringSecretFormatLiteral = Literal[SecretFormat.STRING]

OptionalStringSecretFormatLiteral = Optional[StringSecretFormatLiteral]

SecretFormatLiteral = Literal[SecretFormat.BYTES, SecretFormat.STRING]

OptionalSecretFormatLiteral = Optional[SecretFormatLiteral]

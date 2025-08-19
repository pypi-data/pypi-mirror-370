from typing import Literal, Optional
from maleo.soma.enums.hash import Mode

ObjectModeLiteral = Literal[Mode.OBJECT]

OptionalObjectModeLiteral = Optional[ObjectModeLiteral]

DigestModeLiteral = Literal[Mode.DIGEST]

OptionalDigestModeLiteral = Optional[DigestModeLiteral]

ModeLiteral = Literal[Mode.OBJECT, Mode.DIGEST]

OptionalModeLiteral = Optional[ModeLiteral]

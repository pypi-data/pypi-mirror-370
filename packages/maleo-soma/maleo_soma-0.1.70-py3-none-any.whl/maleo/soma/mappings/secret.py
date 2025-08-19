from typing import Dict
from maleo.soma.enums.secret import SecretFormat

FORMAT_TYPE_MAPPING: Dict[str, type] = {
    SecretFormat.BYTES: bytes,
    SecretFormat.STRING: str,
}

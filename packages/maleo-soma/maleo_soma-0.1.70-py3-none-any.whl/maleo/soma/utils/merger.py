from collections.abc import Mapping
from typing import Dict, Any


def merge_dicts(*obj: Dict[str, Any]) -> Dict[str, Any]:
    def _merge(a: Mapping[str, Any], b: Mapping[str, Any]) -> Dict[str, Any]:
        result = dict(a)  # create a mutable copy
        for key, value in b.items():
            if (
                key in result
                and isinstance(result[key], Mapping)
                and isinstance(value, Mapping)
            ):
                result[key] = _merge(result[key], value)
            else:
                result[key] = value
        return result

    merged: Dict[str, Any] = {}
    for ob in obj:
        merged = _merge(merged, ob)
    return merged

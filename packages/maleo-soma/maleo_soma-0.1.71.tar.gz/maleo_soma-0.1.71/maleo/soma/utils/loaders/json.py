import json
from pathlib import Path
from typing import Union
from maleo.soma.types.base import ListOrDictOfAny


def from_path(path: Union[Path, str]) -> ListOrDictOfAny:
    file_path = Path(path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r") as f:
        return json.load(f)


def from_string(string: str) -> ListOrDictOfAny:
    return json.loads(string)

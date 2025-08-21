import yaml
from pathlib import Path
from typing import Union
from maleo.soma.types.base import ListOrDictOfAny


def from_path(path: Union[Path, str]) -> ListOrDictOfAny:
    file_path = Path(path)

    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    with file_path.open("r") as f:
        return yaml.safe_load(f)


def from_string(string: str) -> ListOrDictOfAny:
    return yaml.safe_load(string)

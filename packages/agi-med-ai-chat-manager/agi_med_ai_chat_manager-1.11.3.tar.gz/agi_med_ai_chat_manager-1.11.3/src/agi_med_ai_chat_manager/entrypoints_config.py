from pydantic import BaseModel, AfterValidator
from typing import Annotated, Dict


def check_corresponding_keys(dictionary):
    for key, v in dictionary.items():
        if key == v.key:
            continue
        raise ValueError(f"mismatch of {key=} and {v.key=}")
    return dictionary


class EntrypointConfig(BaseModel):
    key: str
    name: str
    caption: str
    args: Dict[str, str | bool | int]


Entrypoints = Annotated[Dict[str, EntrypointConfig], AfterValidator(check_corresponding_keys)]


class EntrypointsConfig(BaseModel):
    entrypoints: Entrypoints
    default_entrypoint_key: str
    warmup: bool

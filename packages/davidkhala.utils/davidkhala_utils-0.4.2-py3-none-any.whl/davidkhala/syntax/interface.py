from abc import ABC
from dataclasses import dataclass
from typing import Any


class Serializable:

    def as_dict(self) -> dict:
        return self.__dict__

    def __str__(self):
        return str(vars(self))


@dataclass
class DataClass(ABC):
    ...


class Delegate:
    def __init__(self, client: Any) -> None:
        self.client = client

    def __getattr__(self, name):
        # Delegate unknown attributes/methods to the wrapped instance
        return getattr(self.client, name)

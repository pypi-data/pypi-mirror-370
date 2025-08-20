from dataclasses import dataclass
from typing import Any, Generic, TypeVar

INNER_TYPE = TypeVar("INNER_TYPE")

@dataclass(kw_only=True)
class Wrapper(Generic[INNER_TYPE]):
    inner_obj: INNER_TYPE

    @staticmethod
    def make(INNER_TYPE)->"INNER_TYPE":
        return Wrapper(INNER_TYPE)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner_obj, name)
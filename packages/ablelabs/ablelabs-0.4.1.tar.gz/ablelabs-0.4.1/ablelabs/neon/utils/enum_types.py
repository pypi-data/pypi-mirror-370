from enum import Enum, IntFlag, auto
from enum import IntEnum as BaseIntEnum
from typing import Callable, Generic, TypeVar, Any


class StrEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, value: str):
        return cls[value.upper()]


class IntEnum(BaseIntEnum):
    def __str__(self):
        return f"{self.name}({self.value})"


class ValueEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        return self.value

    def __str__(self):
        return str(self.value)


T = TypeVar("T")


class ItemGetable(property, Generic[T]):
    def __init__(self, wrapped: Callable[[T], Any]):
        super().__init__(lambda s: self)
        self.wrapped: Callable[[T], Any] = wrapped

    def __getitem__(self, item: T) -> Any:
        return self.wrapped(item)

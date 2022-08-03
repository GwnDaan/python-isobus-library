from abc import ABC, abstractmethod
from dataclasses import dataclass, fields


@dataclass
class DataObject(ABC):
    def __post_init__(self):
        _validate(self)

    @abstractmethod
    def get_data(self) -> bytes:
        """Get this object as data to transmit it over ISOBUS."""
        raise NotImplementedError()


def _validate(instance):
    for field in fields(instance):
        attr = getattr(instance, field.name)
        if not isinstance(attr, field.type):
            raise ValueError(f"Field '{field.name}' is type {type(attr)}, but should be {field.type}")

from dataclasses import dataclass, field

from ..packet_utils import object_to_bytes
from .abstract_object import DataObject


@dataclass
class SoftKeyObject(DataObject):
    _TYPE = 5  # Byte 3

    object_id: int  # Byte 1-2
    background_color: int  # Byte 4
    key_code: int  # Byte 5
    objects: list = field(default_factory=list)  # Number of objects = byte 5, repeated with starting byte 7
    macros: list = field(default_factory=list)  # Number of macros = byte 6, repeated after objects

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes(
            [
                self.object_id,
                self._TYPE,
                self.background_color,
                self.key_code,
                len(self.objects),
                len(self.macros),
                self.objects,
                self.macros,
            ],
            # The following are the byte_length of each data value
            2,
            1,
            1,
            1,
            1,
            1,
            6,
            2,
        )

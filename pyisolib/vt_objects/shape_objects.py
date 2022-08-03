from dataclasses import dataclass, field

from ..packet_utils import object_to_bytes
from .abstract_object import DataObject


@dataclass
class LineObject(DataObject):
    _TYPE = 13  # Byte 3

    object_id: int  # Byte 1-2
    line_attributes: int  # Byte 4-5
    width: int  # Byte 6-7
    height: int  # Byte 8-9
    line_direction: int  # Byte 10
    macros: list = field(default_factory=list)  # Number of macros = byte 11, repeated with starting byte 12

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes(
            [self.object_id, self._TYPE, self.line_attributes, self.width, self.height, self.line_direction, len(self.macros), self.macros],
            # The following are the byte_length of each data value
            2,
            1,
            2,
            2,
            2,
            1,
            1,
            2,
        )


@dataclass
class RectangleObject(DataObject):
    _TYPE = 14  # Byte 3

    object_id: int  # BYte 1-2
    line_attributes: int  # Byte 4-5
    width: int  # Byte 6-7
    height: int  # Byte 8-9
    line_suppresion: int  # Byte 10
    fill_attributes: int  # Byte 11-12
    macros: list = field(default_factory=list)  # Number of macros = byte 13, repeated with starting byte 14

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes(
            [self.object_id, self._TYPE, self.line_attributes, self.width, self.height, self.line_suppresion, self.fill_attributes, len(self.macros), self.macros],
            # The following are the byte_length of each data value
            2,
            1,
            2,
            2,
            2,
            1,
            2,
            1,
            2,
        )

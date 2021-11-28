from dataclasses import dataclass, field

from ..packet_utils import object_to_bytes
from .abstract_object import DataObject


@dataclass
class ButtonObject(DataObject):
    _TYPE = 6 # Byte 3
    
    object_id: int # Byte 1-2
    width: int # Byte 4-5
    height: int # Byte 6-7
    background_color: int # Byte 8
    border_color: int # Byte 9
    key_code: int # Byte 10
    options: int # Byte 11
    
    objects: list = field(default_factory=list) # Number of objects = byte 5, repeated with starting byte 7
    macros: list = field(default_factory=list) # Number of macros = byte 6, repeated after objects
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.width, self.height, self.background_color, self.border_color, self.key_code, self.options,
                                len(self.objects), len(self.macros), self.objects, self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 2, 2, 1, 1, 1, 1, 1, 1, 6, 2)

@dataclass
class PointerObject(DataObject):
    _TYPE = 27 # Byte 3
    
    object_id: int # Byte 1-2
    value: int # Byte 4-5
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.value],
                               # The following are the byte_length of each data value
                               2, 1, 2)

@dataclass
class MacroObject(DataObject):
    _TYPE = 28 # Byte 3
    
    object_id: int # Byte 1-2
    command: bytes # Byte 4-5
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, len(self.command), self.command],
                               # The following are the byte_length of each data value
                               2, 1, 2, len(self.command))
from dataclasses import dataclass, field

from ..packet_utils import SignedInt, object_to_bytes
from .abstract_object import DataObject

@dataclass
class _OutputFieldObject(DataObject):
    object_id: int # Byte 1-2
    width: int # Byte 4-5
    height: int # Byte 6-7
    background_color: int # Byte 8
    font_attributes: int # Byte 9-10
    options: int # Byte 11
    
    # Overrides from DataObject
    def get_data(self, type):
        return object_to_bytes([self.object_id, type, self.width, self.height, self.background_color, self.font_attributes, self.options],
                               # The following are the byte_length of each data value
                               2, 1, 2, 2, 1, 2, 1)
    
@dataclass
class StringObject(_OutputFieldObject):
    _TYPE = 11 # Byte 3
    
    string_variable: int # Byte 12-13
    justification: int # Byte 14
    length: int # Byte 15-16
    value: str # Starting from byte 17
    
    macros:list = field(default_factory=list) # Number of macros = byte after value, repeated after byte of number of macros
    
    # Overrides from _OutputFieldObject
    def get_data(self):
        data = object_to_bytes([self.string_variable, self.justification, self.length, self.value, len(self.macros), self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 2, len(self.value), 1, 2)
        return super().get_data(self._TYPE) + data

@dataclass
class NumberObject(_OutputFieldObject):
    """The VT uses the following equation to display the value:
    displayedValue =  (value + offset) * scaling_factor"""
    _TYPE = 12 # Byte 3
    
    number_variable: int # Byte 12-13
    value: int # Byte 14-17
    offset: int # Byte 18-21, NOTE: need to convert to SignedInteger
    scale: float # Byte 22-25
    number_of_decimals: int # Byte 26
    format: int # 27
    justification: int # 28

    macros:list = field(default_factory=list) # Number of macros = byte 29, repeated with starting byte 30
    
    # Overrides from _OutputFieldObject
    def get_data(self):
        data = object_to_bytes([self.number_variable, self.value, SignedInt(self.offset), self.scale, self.number_of_decimals, self.format, self.justification, len(self.macros), self.macros],
                               # The following are the byte_length of each data value
                               2, 4, 4, 4, 1, 1, 1, 1, 2)
        return super().get_data(self._TYPE) + data
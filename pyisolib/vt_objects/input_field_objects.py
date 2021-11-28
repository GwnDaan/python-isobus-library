from dataclasses import dataclass, field

from ..packet_utils import object_to_bytes
from .abstract_object import DataObject

@dataclass
class BoolInputObject(DataObject):
    _TYPE = 7 # Byte 3
    
    object_id: int # Byte 1-2
    background_color: int # Byte 4
    width: int # Byte 5-6
    foreground_color: int # Byte 7-8
    bool_variable: int # Byte 9-10
    value: bool # Byte 11
    enabled: bool # Byte 12
    
    macros: list = field(default_factory=list) # Number of macros = byte 13, repeated with starting byte 14
    
    # Overrides from DataObject
    def get_data(self, type):
        return object_to_bytes([self.object_id, type, self.background_color, self.width, self.foreground_color, self.bool_variable, self.value, self.enabled, len(self.macros), self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 1, 2, 2, 2, 1, 1, 1, 2)
        
@dataclass
class NumberInputObject(DataObject):
    _TYPE = 9 # Byte 3
    
    object_id: int # Byte 1-2
    width: int # Byte 4-5
    height: int # Byte 6-7
    background_color: int # Byte 8
    font_attributes: int # Byte 9-10
    options: int # Byte 11
    
    number_variable: int # Byte 12-13
    value: int # Byte 14-17
    min_value: int # Byte 18-21
    max_value: int # Byte 22-25
    offset: int # Byte 26-29
    scale: int # byte 30-33
    number_of_decimals: int # Byte 34
    format: int # Byte 35
    justification: int # Byte 36
    options2: int # Byte 37
    
    macros: list = field(default_factory=list) # Number of macros = byte 38, repeated with starting byte 39

    # Overrides from _InputFieldObject
    def get_data(self):
        part1 = object_to_bytes([self.object_id, self._TYPE, self.width, self.height, self.background_color, self.font_attributes, self.options],
                               # The following are the byte_length of each data value
                               2, 1, 2, 2, 1, 2, 1)
        part2 = object_to_bytes([self.number_variable, self.value, self.min_value, self.max_value, self.offset, self.scale, 
                                self.number_of_decimals, self.format, self.justification, self.options2, len(self.macros), self.macros],
                               # The following are the byte_length of each data value
                               2, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 2)
        return part1 + part2
    
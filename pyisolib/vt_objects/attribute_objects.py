from dataclasses import dataclass, field

from .object_utils import object_to_bytes
from .abstract_object import DataObject

@dataclass
class FontAttributes(DataObject):
    _TYPE = 23 # Byte 3
    
    object_id: int # Byte 1-2
    font_color: int # Byte 4
    font_size: int # Byte 5
    font_type: int # Byte 6
    font_style: int # Byte 7
    
    macros: list = field(default_factory=list) # Number of macros = byte 8, repeated with starting byte 9
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.font_color, self.font_size, self.font_type, self.font_style, len(self.macros), self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 1, 1, 1, 1, 1, 1, 1)

@dataclass
class LineAttribute(DataObject):
    _TYPE = 24 # Byte 3
    
    object_id: int # Byte 1-2
    line_color: int # Byte 4
    line_width: int # Byte 5
    line_art: int # Byte 6-7
    
    macros: list = field(default_factory=list) # Number of macros = byte 8, repeated with starting byte 9
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.line_color, self.line_width, self.line_art, len(self.macros), self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 1, 1, 2, 1, 2)

@dataclass
class FillAttribute(DataObject):
    _TYPE = 25 # Byte 3
    
    object_id: int # Byte 1-2
    fill_type: int # Byte 4
    fill_color: int # Byte 5
    fill_pattern: int # Byte 6-7
    
    macros: list = field(default_factory=list) # Number of macros = byte 8, repeated with starting byte 9
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.fill_type, self.fill_color, self.fill_pattern, len(self.macros), self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 1, 1, 2, 1, 2)
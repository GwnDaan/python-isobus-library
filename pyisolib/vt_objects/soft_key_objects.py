from dataclasses import dataclass, field

from .object_utils import object_to_bytes
from .abstract_object import DataObject
     
@dataclass
class SoftKeyObject(DataObject):    
    _TYPE = 5 # Byte 3
    
    object_id: int # Byte 1-2
    background_color: int # Byte 4
    key_code: int # Byte 5
    objects: list = field(default_factory=list) # Number of objects = byte 5, repeated with starting byte 7
    macros: list = field(default_factory=list) # Number of macros = byte 6, repeated after objects
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.background_color, self.key_code, len(self.objects), len(self.macros), self.objects, self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 1, 1, 1, 1, 6, 2)
    
# TODO Determine in which file we place the button object
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
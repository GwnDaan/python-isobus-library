from dataclasses import dataclass
from .abstract_object import DataObject
from ..packet_utils import object_to_bytes

@dataclass
class StringVariable(DataObject):
    _TYPE = 22 # Byte 3
    
    object_id: int # Byte 1-2
    length: int # Byte 4-5
    value: str # Starting from byte 6

    # Overrides from DataObject
    def get_data(self):
        value = self.value
        if len(value) < self.length:
            value += (' ' for _ in range(self.length - len(value)))
        elif len(value) > self.length:
            raise ValueError(f"The length field ({self.length} is not equal to the lenght of the value", len(value))
        
        return object_to_bytes([self.object_id, self._TYPE, self.length, self.value], 
                               # The following are the byte_length of each data value
                               2, 1, 2, len(self.value))

@dataclass
class NumberVariable(DataObject):
    _TYPE = 21 # Byte 3
    
    object_id: int # Byte 1-2
    value: str # Byte 4-7

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.value], 
                               # The following are the byte_length of each data value
                               2, 1, 4)

@dataclass
class BoolVariable(NumberVariable):
    """NOTE: this is not an object specified by the ISOBUS standard, but is implemented for easier usage"""

    value: bool # Byte 4-7

    # Overrides from NumberVariable
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, 1 if self.value else 0], 
                               # The following are the byte_length of each data value
                               2, 1, 4)
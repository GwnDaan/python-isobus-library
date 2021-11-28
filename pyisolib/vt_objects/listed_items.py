
from dataclasses import dataclass
from .abstract_object import DataObject
from ..packet_utils import SignedInt, object_to_bytes

@dataclass
class ListedObject(DataObject):
    object_id: int
    x_location: int
    y_location: int
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, SignedInt(self.x_location), SignedInt(self.y_location)], 2, 2, 2)

@dataclass
class ListedMacro(DataObject):
    event_id: int
    macro_id: int

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.event_id, self.macro_id], 1, 1)
    
@dataclass
class ListedLanguage(DataObject):
    language_code: str

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.language_code], 2)
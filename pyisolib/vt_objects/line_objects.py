import dataclasses

from .object_utils import SignedInt, object_to_bytes
from .abstract_object import DataObject


@dataclasses
class ListedObject(DataObject):
    object_id: int
    x_location: int
    y_location: int
    
    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, SignedInt(self.x_location), SignedInt(self.y_location)], 2, 2, 2)
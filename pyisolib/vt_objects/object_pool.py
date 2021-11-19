from vt_objects.abstract_object import DataObject
from vt_objects.top_level_objects import DataMaskObject, WorkingSetObject

class ObjectPool:
    
    def __init__(self):
        self._objects = []
        
    def add_object(self, object):
        if not isinstance(object, DataObject):
            raise RuntimeError(f"Expected instance of DataObject but found {type(object)}")
        self._objects.append(object)
    
    def is_ready(self):
        """Returns true if the pool is ready for transmission"""
        object_types = (type(object) for object in self._objects)
        return WorkingSetObject in object_types and DataMaskObject in object_types
    
    def get_data(self):
        """Get this pool as data to transmit it over ISOBUS."""
        result = bytes()
        for object in self._objects:
            result += object.get_data()
        return result
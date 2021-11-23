from .abstract_object import DataObject
from .top_level_objects import DataMaskObject, WorkingSetObject

class ObjectPool:
    
    def __init__(self):
        self._objects = []
        self.cached_data = None
        
    def add_object(self, object):
        if not isinstance(object, DataObject):
            raise RuntimeError(f"Expected instance of DataObject but found {type(object)}")
        self._objects.append(object)
    
    def is_ready(self):
        """Returns true if the pool is ready for transmission"""
        object_types = (type(object) for object in self._objects)
        return WorkingSetObject in object_types and DataMaskObject in object_types and self.cached_data is not None
        
    def cache_data(self):
        """Get this pool as data to transmit it over ISOBUS."""
        result = bytes()
        for object in self._objects:
            result += object.get_data()
        self.cached_data = result # Set it after we got all data as it might return errors and then is_ready will flag incorrectly
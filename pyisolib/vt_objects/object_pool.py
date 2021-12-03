from dataclasses import fields
from .abstract_object import DataObject
from .top_level_objects import DataMaskObject, WorkingSetObject

class ObjectPool:
    
    def __init__(self):
        self._objects = []
        self.file_name = None
        self.cached_data = None
        
    def add_object(self, object):
        if not isinstance(object, DataObject):
            raise RuntimeError(f"Expected instance of DataObject but found {type(object)}")
        self._objects.append(object)
    
    def is_ready(self):
        """Returns true if the pool is ready for transmission"""
        object_types = (type(object) for object in self._objects)
        return ((WorkingSetObject in object_types and DataMaskObject in object_types) or self.file_name is not None) and self.cached_data is not None
        
    def cache_data(self):
        """Get this pool as data to transmit it over ISOBUS."""
        if self.file_name is not None:
            # We read from the file instead
            with open(self.file_name, 'rb') as file:
                self.cached_data = file.read()
        else:
            result = bytearray()
            for object in self._objects:
                result.extend(object.get_data())
            self.cached_data = bytes(result) # Set it after we got all data as it might return errors and then is_ready will flag incorrectly
    
    @staticmethod
    def save_pooldata_to_file(pool_class, file_name):
        result = bytearray()
        for field in fields(pool_class):
            object = field.default
            print(type(object))
            if not isinstance(object, DataObject):
                raise ValueError(f"Expected instance of DataObject but found {type(object)}")
            
            result.extend(object.get_data())
            
        file = open(file_name, 'wb')
        file.write(result)
        
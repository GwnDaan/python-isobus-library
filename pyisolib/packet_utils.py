from dataclasses import dataclass

from .abstract_object import DataObject

def object_to_bytes(data: list, *byte_length) -> bytes:
    """Converts an complete object in the form of a list to bytes
    NOTE: the length of data and byte_length should be the same!
    :param list data:
        The list with data
    :param byte_length:
        Specifies how many bytes each value in data should be
    """
    if len(data) > 0 and len(data) != len(byte_length):
        raise RuntimeError("The length of data is not equal to the length of byte_length", data, byte_length)
    
    result = bytes(0)
    for i in range(len(data)):
        # We do each type seperately
        
        value = data[i]
        length = byte_length[i]
        if isinstance(value, int):
            # Make sure that we have the int byte_length type
            if not isinstance(length, int):
                raise RuntimeError("We got an invalid byte_length type for 'int' data", length)
            result += value.to_bytes(length, 'little')
        
        elif isinstance(value, SignedInt):
            # Make sure that we have the int byte_length type
            if not isinstance(length, int):
                raise RuntimeError("We got an invalid byte_length type for 'int' data", length)
            result += value.get_data(length)
        
        elif isinstance(value, bool):
            if (length != 1):
                raise RuntimeError("We got type bool but byte_length is not '1'", length)
            result += bytes(1) if value else bytes(0)
        
        elif isinstance(value, str):
            # Make sure that we have the int byte_length type
            if not isinstance(length, int):
                raise RuntimeError("We got an invalid byte_length type for 'int' data", length)
            
            #TODO figure out if this is the correct way of displaying string
            encoded = value.encode('iso-8859-1')
            if len(encoded) != length:
                raise RuntimeError(f"The lenth of our encoded string ({len(encoded)}) is not equal to", length)
            result += encoded
        
        elif isinstance(value, list):            
            # We generate new byte_lengths for each element in the list            
            result += object_to_bytes(value, *(length for _ in range(len(value))))
        
        elif isinstance(value, bytes) or isinstance(value, bytearray):
            if (length != len(value)):
                raise RuntimeError(f"We got type bytes but byte_length is not equal to length of bytes ({len(value)})", length)
            result += value
        
        elif isinstance(value, DataObject):
            # Make sure that we have the int byte_length type
            if not isinstance(length, int):
                raise RuntimeError("We got an invalid byte_length type for 'int' data", length)
            
            converted = value.get_data()
            if len(converted) != length:
                raise RuntimeError(f"The converted length ({len(converted)}) was not equal to the length provided: ", length)
            result += converted
            
        else:
            raise RuntimeError("We couldn't process the following type", type(value))
    
    return result
    
@dataclass
class SignedInt(DataObject):
    value: int
    
    # Overrides from DataObject
    def get_data(self, length) -> bytes:
        return self.value.to_bytes(length, 'little', signed=True)
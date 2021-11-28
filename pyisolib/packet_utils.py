from dataclasses import dataclass

from .vt_objects.abstract_object import DataObject

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
                raise RuntimeError("We got an invalid byte_length type for 'signedint' data", length)
            result += value.get_data(length)

        elif isinstance(value, float):
            # Make sure that we have the int byte_length type
            if length != 4:
                raise RuntimeError("We got type float but byte_length is not '4'", length)
            result += IEEE754(value)
        
        elif isinstance(value, bool):
            if length != 1:
                raise RuntimeError("We got type bool but byte_length is not '1'", length)
            result += bytes(1) if value else bytes(0)
        
        elif isinstance(value, str):
            # Make sure that we have the int byte_length type
            if not isinstance(length, int):
                raise RuntimeError("We got an invalid byte_length type for 'str' data", length)
            
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

#TODO: below is copied and therefore only for testing
# Function for converting decimal to binary
def float_bin(my_number, places = 3):
    my_whole, my_dec = str(my_number).split(".")
    my_whole = int(my_whole)
    res = (str(bin(my_whole))+".").replace('0b','')
 
    for x in range(places):
        my_dec = str('0.')+str(my_dec)
        temp = '%1.20f' %(float(my_dec)*2)
        my_whole, my_dec = temp.split(".")
        res += my_whole
    return res
 
def IEEE754(n):
    # identifying whether the number
    # is positive or negative
    sign = 0
    if n < 0 :
        sign = 1
        n = n * (-1)
    p = 30
    # convert float to binary
    dec = float_bin (n, places = p)
 
    dotPlace = dec.find('.')
    onePlace = dec.find('1')
    # finding the mantissa
    if onePlace > dotPlace:
        dec = dec.replace(".","")
        onePlace -= 1
        dotPlace -= 1
    elif onePlace < dotPlace:
        dec = dec.replace(".","")
        dotPlace -= 1
    mantissa = dec[onePlace+1:]
 
    # calculating the exponent(E)
    exponent = dotPlace - onePlace
    exponent_bits = exponent + 127
 
    # converting the exponent from
    # decimal to binary
    exponent_bits = bin(exponent_bits).replace("0b",'')
 
    mantissa = mantissa[0:23]
 
    # the IEEE754 notation in binary    
    final = str(sign) + exponent_bits.zfill(8) + mantissa
 
    # convert the binary to hexadecimal
    # hstr = '0x%0*X' %((len(final) + 3) // 4, int(final, 2))
    # return (hstr, final)
    return int(final, 2).to_bytes(len(final) // 8, byteorder='big')
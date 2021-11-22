from dataclasses import dataclass, field

from .abstract_object import DataObject
from .object_utils import object_to_bytes

from PIL import Image

@dataclass
class GraphicsObject(DataObject):
    _TYPE = 20 # Byte 3
    
    object_id: int # Byte 1-2
    new_width: int # Byte 4-5
    format: int # Byte 10
    # options: int # Byte 11
    transparency_color: int # Byte 12
    image_path: str
    macros :list = field(default_factory=list) # Number of macros = byte 14, repeated after 'objects'
    
    # Overrides from DataObject
    def get_data(self):
        raw_picture_data = self._get_raw_image_data()
        encoded_picture_data = _run_length_encoding(raw_picture_data)
        
        # useEncoded = len(encoded_picture_data) < len(raw_picture_data)
        useEncoded = False
        picture_data = encoded_picture_data if useEncoded else raw_picture_data

        # TODO: better way of allowing options to be set
        # if len(encoded_picture_data) < len(raw_picture_data):
            # self.options = 4
        self.options = 0
        
        # TODO: this is testing
        picture_data = bytearray()
        for i in range(216):
          picture_data.append(16 + i)
        
        data = object_to_bytes([self.object_id, self._TYPE, self.new_width, 27, 8, self.format, self.options, self.transparency_color, len(picture_data), len(self.macros), picture_data, self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 2, 2, 2, 1, 1, 1, 4, 1, len(picture_data), 2)

        return data
    
    def _get_raw_image_data(self) -> bytes:
        image = Image.open(self.image_path)
        image.load()
                
        image = image.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=216)
        
        self.picture_width = image.width
        self.picture_height = image.height

        data = bytearray()
        for y in range(self.picture_height):
          for x in range(self.picture_width):
            data.append(15 + 216 - image.getpixel((x, y)))
        return data
    
def _run_length_encoding(data):
  compressed = bytearray()
  
  # Current info
  count = 1
  color = data[0]
  
  for i in range(1,len(data)):
    if data[i] == color and count < 255:
      count = count + 1
    else:
      compressed.append(count)
      compressed.append(color)
      color = data[i]
      count = 1
    
  # Append the current info as we didn't do that yet
  compressed.append(count)
  compressed.append(color)
  return bytes(compressed)
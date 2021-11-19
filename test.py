# WORKING SET (Alle objects zijn de 'voorpagina')

from vt_objects.graphics_objects import GraphicsObject
from vt_objects.listed_items import ListedObject
from vt_objects.object_utils import SignedInt
from vt_objects.top_level_objects import DataMaskObject, WorkingSetObject

# DATA MASK (De daarwerkelijke besturing)
header = (1).to_bytes(2, 'little') + \
    bytes([1, 100]) + (65535).to_bytes(2, 'little') + bytes([1, 0])
objects = (20).to_bytes(2, 'little') + (0).to_bytes(2, 'little',
                                                signed=True) + (0).to_bytes(2, 'little', signed=True)
data1 = header + objects

data2 = DataMaskObject(1, 100, 65535, [ListedObject(20, 0, 0)])

# print(data1)
# print(data2.get_data())
# print(data1 == data2.get_data())

    
test = GraphicsObject(1, 100, 100, 100, 2, 0, 0, 'assets/800x600 test.png')
print(test.get_data())
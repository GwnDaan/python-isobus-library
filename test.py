# WORKING SET (Alle objects zijn de 'voorpagina')

from vt_objects.listed_items import ListedObject
from vt_objects.object_utils import SignedInt
from vt_objects.top_level_objects import WorkingSetObject

header = (2002).to_bytes(2, 'little') + \
    bytes([0, 50, 1]) + (1).to_bytes(2, 'little') + bytes([1, 0, 0])
objects = (20).to_bytes(2, 'little') + (0).to_bytes(2, 'little',
                                                    signed=True) + (0).to_bytes(2, 'little', signed=True)
data1 = header + objects

data2 = WorkingSetObject(2002, 50, True, 1, [ListedObject(20, 0, 0)])

print(data1)
print(data2.get_data())
print(data1 == data2.get_data())
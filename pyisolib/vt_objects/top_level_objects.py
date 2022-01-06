from dataclasses import dataclass, field

from .abstract_object import DataObject
from .listed_items import ListedObject
from ..packet_utils import object_to_bytes


@dataclass
class WorkingSetObject(DataObject):
    _TYPE = 0  # Byte 3

    object_id: int  # Byte 1-2
    background_color: int  # Byte 4
    selectable: bool  # 5
    active_mask_object_id: int  # Byte 6-7
    objects: list  # Number of objects = byte 8, repeated with starting byte 11
    macros: list = field(default_factory=list)  # Number of macros = byte 9, repeated after 'objects'
    languages: list = field(default_factory=list)  # Number of languages = byte 10, repeated after 'macros'

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.background_color, self.selectable, self.active_mask_object_id, len(self.objects), len(self.macros), len(self.languages), self.objects, self.macros, self.languages],
                               # The following are the byte_length of each data value
                               2, 1, 1, 1, 2, 1, 1, 1, 6, 2, 2)


@dataclass
class DataMaskObject(DataObject):
    _TYPE = 1  # Byte 3

    object_id: int  # Byte 1-2
    background_color: int  # Byte 4
    soft_key_mask: int  # Byte 5-6
    objects: list = field(default_factory=list)  # Number of objects = byte 7, repeated with starting byte 9
    macros: list = field(default_factory=list)  # Number of macros = byte 8, repeated after 'objects'

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.background_color, self.soft_key_mask, len(self.objects), len(self.macros), self.objects, self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 1, 2, 1, 1, 6, 2)


@dataclass
class SoftKeyMaskObject(DataObject):
    '''NOTE: objects field doesn't take the normal ListedObject class but instead just integers referring to the object id'''

    _TYPE = 4  # Byte 3

    object_id: int  # Byte 1-2
    background_color: int  # Byte 4
    objects: list = field(default_factory=list)  # Number of objects = byte 5, repeated with starting byte 7
    macros: list = field(default_factory=list)  # Number of macros = byte 6, repeated after objects

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.background_color, len(self.objects), len(self.macros), self.objects, self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 1, 1, 1, 2, 2)


@dataclass
class AlarmMaskObject(DataObject):
    _TYPE = 2  # Byte 3

    object_id: int  # Byte 1-2
    background_color: int  # Byte 4
    soft_key_mask: int  # Byte 5-6
    priorty: int  # Byte 7
    acoustic_signal: int  # Byte 8

    objects: list = field(default_factory=list)  # Number of objects = byte 9, repeated with starting byte 11
    macros: list = field(default_factory=list)  # Number of macros = byte 10, repeated after objects

    # Overrides from DataObject
    def get_data(self):
        return object_to_bytes([self.object_id, self._TYPE, self.background_color, self.soft_key_mask, self.priorty, self.acoustic_signal, len(self.objects), len(self.macros), self.objects, self.macros],
                               # The following are the byte_length of each data value
                               2, 1, 1, 2, 1, 1, 1, 1, 6, 2)

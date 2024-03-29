from dataclasses import dataclass, field

from .abstract_object import DataObject
from ..packet_utils import object_to_bytes

from PIL import Image


@dataclass
class GraphicsObject(DataObject):
    _TYPE = 20  # Byte 3

    object_id: int  # Byte 1-2
    new_width: int  # Byte 4-5
    format: int  # Byte 10 # TODO: implement format
    # options: int # Byte 11
    transparency_color: int  # Byte 12 # TODO: implement in options
    image_path: str
    macros: list = field(default_factory=list)  # Number of macros = byte 14, repeated after 'objects'

    # Overrides from DataObject
    def get_data(self):
        raw_picture_data = self._get_raw_image_data()
        encoded_picture_data = _run_length_encoding(raw_picture_data)

        useEncoded = len(encoded_picture_data) < len(raw_picture_data)
        picture_data = encoded_picture_data if useEncoded else raw_picture_data

        # TODO: better way of allowing options to be set
        if len(encoded_picture_data) < len(raw_picture_data):
            self.options = 4
        else:
            self.options = 0

        data = object_to_bytes(
            [
                self.object_id,
                self._TYPE,
                self.new_width,
                self.picture_width,
                self.picture_height,
                self.format,
                self.options,
                self.transparency_color,
                len(picture_data),
                len(self.macros),
                picture_data,
                self.macros,
            ],
            # The following are the byte_length of each data value
            2,
            1,
            2,
            2,
            2,
            1,
            1,
            1,
            4,
            1,
            len(picture_data),
            2,
        )

        return data

    def _get_raw_image_data(self) -> bytes:
        image = Image.open(self.image_path)
        image.load()

        image = image.convert("RGB")

        self.picture_width = image.width
        self.picture_height = image.height

        data = bytearray()
        for y in range(self.picture_height):
            for x in range(self.picture_width):
                r, g, b = image.getpixel((x, y))

                data.append(16 + _get_websafe(r, g, b))
        return data


tbl = tuple((int(i) + 25) // 51 for i in range(256))


def _get_websafe(*color):
    r, g, b = (tbl[c] for c in color)
    return r * 36 + g * 6 + b


def _run_length_encoding(data):
    compressed = bytearray()

    # Current info
    count = 1
    color = data[0]

    for i in range(1, len(data)):
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

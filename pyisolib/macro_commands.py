from .functions import Commands
from .packet_utils import object_to_bytes


def __convert_cmd(*args, completer=0xFF) -> bytes:
    data = bytes(0)
    for element in args:
        data += element if isinstance(element, bytes) else bytes([element])

    # We only need to complete if len of data is less than 8.
    # The transport protocol and extended transport protocol will handle it themselves
    if len(data) < 8:
        data += bytes((completer for _ in range(8 - len(data))))

    return data

# ----------------------
# All the different cmds
# ----------------------


def convert_numericvalue_cmd(object_id, new_value) -> bytes:
    return __convert_cmd(Commands.CHANGE_NUMERIC_VALUE,
                         # Data follows below
                         object_to_bytes([object_id, 0xFF, new_value],
                                         # Byte-length follows below
                                         2, 1, 4))


def change_size_cmd(object_id, new_width, new_height) -> bytes:
    return __convert_cmd(Commands.CHANGE_SIZE,
                         # Data follows below
                         object_to_bytes([object_id, new_width, new_height],
                                         # Byte-length follows below
                                         2, 2, 2))


def change_active_mask_cmd(object_id, new_mask_id) -> bytes:
    return __convert_cmd(Commands.CHANGE_ACTIVE_MASK,
                         # Data follows below
                         object_to_bytes([object_id, new_mask_id],
                                         # Byte-length follows below
                                         2, 2))

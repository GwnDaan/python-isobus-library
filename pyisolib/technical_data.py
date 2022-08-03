from dataclasses import dataclass


@dataclass
class TechnicalData:
    vt_version: int = None

    # Width and height of available data mask
    screen_width: int = None  # in pixels
    screen_height: int = None  # in pixels

    # Width and height of soft key descriptor
    soft_key_width: int = None  # in pixels
    soft_key_height: int = None  # in pixels

    # Number of physical and virtual soft keys available
    soft_key_virtual_amount: int = None
    soft_key_physical_amount: int = None

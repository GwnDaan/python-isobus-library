from dataclasses import dataclass
import pyisolib.macro_commands as macro_commands
from pyisolib.vt_objects.graphics_objects import GraphicsObject
from pyisolib.vt_objects.abstract_object import DataObject
from pyisolib.vt_objects.attribute_objects import FillAttribute, FontAttributes, LineAttribute
from pyisolib.vt_objects.listed_items import ListedMacro, ListedObject
from pyisolib.vt_objects.object_pool import ObjectPool
from pyisolib.vt_objects.other_objects import MacroObject, PointerObject
from pyisolib.vt_objects.output_field_objects import NumberObject
from pyisolib.vt_objects.shape_objects import RectangleObject
from pyisolib.vt_objects.soft_key_objects import SoftKeyObject
from pyisolib.vt_objects.top_level_objects import AlarmMaskObject, SoftKeyMaskObject, DataMaskObject, WorkingSetObject
from pyisolib.vt_objects.variable_objects import NumberVariable

from main import Values

values = Values()  # We use default values


@dataclass
class PreparedPoolData:

    # Background
    background: DataObject = GraphicsObject(20, 600, 2, 0, "assets/background.png")
    logo: DataObject = GraphicsObject(21, 80, 2, 0, "assets/logo.png")

    # Attributes
    style_line: DataObject = LineAttribute(100, 102, 2, 65535)  # Line with color #FF66666 and width 2
    style_fill: DataObject = FillAttribute(101, 1, 0, 65535)  # Fill with color of line attribute
    style_font: DataObject = FontAttributes(102, 0, 5, 0, 0)

    # Add the flow indicator
    flow_indicator: DataObject = RectangleObject(31, 100, 0, 28, 0, 101)

    # Target throughput number
    target_throughput_variable: DataObject = NumberVariable(300, values.target_throughput)
    target_throughput: DataObject = NumberObject(32, 69, 22, 0, style_font.object_id, 1, target_throughput_variable.object_id, 0, 0, 1.0, 0, False, 0)

    # Sum spread number
    sum_variable: DataObject = NumberVariable(301, values.sum)
    sum: DataObject = NumberObject(33, 69, 22, 0, style_font.object_id, 1, sum_variable.object_id, 0, 0, 1.0, 0, False, 0)

    # Speed number
    speed_variable: DataObject = NumberVariable(302, 0)  # km/h default 0
    speed: DataObject = NumberObject(34, 96, 22, 0, style_font.object_id, 1, speed_variable.object_id, 0, 0, 0.1, 1, False, 0)

    # PTO speed number
    pto_speed_variable: DataObject = NumberVariable(303, 0)  # pto default 0
    pto_speed: DataObject = NumberObject(35, 96, 22, 0, style_font.object_id, 1, pto_speed_variable.object_id, 0, 0, 1.0, 0, False, 0)

    # # Flow number
    # throughput_variable: DataObject = NumberVariable(304, values.current_throughput)
    # throughput: DataObject = NumberObject(36, 37, 22, 0, style_font.object_id, 1, throughput_variable.object_id, 0, 0, 1.0, 0, False, 0)

    # # Weight number
    # weight_variable: DataObject = NumberVariable(305, values.product_weight)
    # weight: DataObject = NumberObject(37, 37, 22, 0, style_font.object_id, 1, weight_variable.object_id, 0, 0, 1.0, 0, False, 0)

    # Top level objects
    datamask: DataObject = DataMaskObject(
        1,
        7,
        2,
        [
            # Background
            ListedObject(background.object_id, 0, 0),
            # Flow indicator
            ListedObject(flow_indicator.object_id, 177, 474),
            # Top info numbers
            ListedObject(target_throughput.object_id, 158, 40),
            ListedObject(sum.object_id, 158, 66),
            ListedObject(speed.object_id, 384, 40),
            ListedObject(pto_speed.object_id, 384, 66),
            # Bottom info numbers
            # ListedObject(throughput.object_id, 290, 523), ListedObject(weight.object_id, 290, 549),
        ],
    )
    workingset: DataObject = WorkingSetObject(2002, 7, True, datamask.object_id, [ListedObject(logo.object_id, 0, 5)])

    # ----------------
    # Add virtual keys
    # ----------------

    # Start stop
    start_icon: DataObject = GraphicsObject(1101, 80, 2, 0, "assets/buttons/start.jpg")
    start_button: DataObject = SoftKeyObject(1100, 0, 1, [ListedObject(start_icon.object_id, 0, 0)], [ListedMacro(25, 200)])  # Soft key for start button

    stop_icon: DataObject = GraphicsObject(1103, 80, 2, 0, "assets/buttons/stop.jpg")
    stop_button: DataObject = SoftKeyObject(1102, 0, 1, [ListedObject(stop_icon.object_id, 0, 0)], [ListedMacro(25, 201)])  # Soft key for stop button

    startstop_pointer: DataObject = PointerObject(1000, stop_button.object_id if values.running else start_button.object_id)  # Create pointer soft key (id=1000)
    to_stop_macro: DataObject = MacroObject(200, macro_commands.convert_numericvalue_cmd(startstop_pointer.object_id, stop_button.object_id))  # Macro to change start to stop button
    to_start_macro: DataObject = MacroObject(201, macro_commands.convert_numericvalue_cmd(startstop_pointer.object_id, start_button.object_id))  # Macro to change stop to start button

    # Auto manual
    manual_icon: DataObject = GraphicsObject(1111, 80, 2, 0, "assets/buttons/manual.jpg")
    manual_button: DataObject = SoftKeyObject(1110, 0, 1, [ListedObject(manual_icon.object_id, 0, 0)], [ListedMacro(25, 202)])  # Create soft key for manual button

    auto_icon: DataObject = GraphicsObject(1113, 80, 2, 0, "assets/buttons/auto.jpg")
    auto_button: DataObject = SoftKeyObject(1112, 0, 1, [ListedObject(auto_icon.object_id, 0, 0)], [ListedMacro(25, 203)])  # Create soft key for automatic button

    automanual_pointer: DataObject = PointerObject(1001, manual_button.object_id if values.automatic else auto_button.object_id)  # Create pointer soft key (id=1001)
    to_auto_macro: DataObject = MacroObject(202, macro_commands.convert_numericvalue_cmd(automanual_pointer.object_id, auto_button.object_id))  # Macro to change manual to auto button
    to_manual_macro: DataObject = MacroObject(203, macro_commands.convert_numericvalue_cmd(automanual_pointer.object_id, manual_button.object_id))  # Macro to change auto to manual button

    # minus throughput
    min_icon: DataObject = GraphicsObject(1120, 80, 2, 0, "assets/buttons/min.png")
    min_button: DataObject = SoftKeyObject(1002, 7, 1, [ListedObject(min_icon.object_id, 0, 0)])  # Create soft key (id=1002) and (child=1120)

    # plus throughput
    plus_icon: DataObject = GraphicsObject(1130, 80, 2, 0, "assets/buttons/plus.png")
    plus_button: DataObject = SoftKeyObject(1003, 7, 1, [ListedObject(plus_icon.object_id, 0, 0)])  # Create soft key (id=1003) and (child=1130)

    # reset sum
    reset_macro: DataObject = MacroObject(204, macro_commands.convert_numericvalue_cmd(sum_variable.object_id, 0))  # Reset the number variable
    reset_icon: DataObject = GraphicsObject(1140, 80, 2, 0, "assets/buttons/reset.png")
    reset_button: DataObject = SoftKeyObject(1004, 7, 1, [ListedObject(reset_icon.object_id, 0, 0)], [ListedMacro(25, reset_macro.object_id)])  # Create soft key (id=1004) and (child=1140)

    # Add keys to mask
    softkeymask: DataObject = SoftKeyMaskObject(
        2, 7, [startstop_pointer.object_id, plus_button.object_id, reset_button.object_id, 65535, 65535, 65535, automanual_pointer.object_id, min_button.object_id]
    )


# Create the cached pool data file to be used on the ECU
if __name__ == "__main__":
    pool_data = PreparedPoolData()
    ObjectPool.save_pooldata_to_file(pool_data, "vtpooldata.bin")

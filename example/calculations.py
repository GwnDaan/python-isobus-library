from dataclasses import dataclass
import logging
import time

from pyisolib.pyisolib import macro_commands
from pyisolib.pyisolib.working_set import WorkingSet

MAX_WIDTH_INDICATOR = 246

CALIBRATION_VALUE = 18.50 * 10  # KG/MIN max
WIDTH = 10


@dataclass
class Values:
    target_throughput: int = 300  # The default flow set to 300
    target_valve_percentage: int = 0  # Assume it's closed. Field should range from 0-100(%)

    # Measured, assume starting position is closed. Field should range from 0-100(%)
    current_valve_percentage: int = 0
    sum: int = 0  # The total sum spread
    last_sum_adjustment: int = 0  # Last update time

    running: bool = False  # Whether or not the machine is currently running
    speed: float = 0  # Assume we are standing still when we have not received data yet
    pto_speed: float = 0  # See above

    automatic: bool = True  # Default automatic weight system to true


def update_valve(values: Values, ws: WorkingSet) -> Values:
    if values.running:

        # Calculate elapsed time since last update
        time_elapsed = time.time() - values.last_sum_adjustment
        values.last_sum_adjustment = time.time()

        # Add to total sum spread based on elapsed time
        values.sum += values.current_valve_percentage / 100 * CALIBRATION_VALUE * time_elapsed / 60
        ws.send_to_vt(macro_commands.convert_numericvalue_cmd(301, int(values.sum)))

        # Area per minute using (speed * width)
        # 60 is for 'km/h' to 'km/min', and 1000 for 'm' to 'km', and 100 for 'km^2' to 'ha'
        ha_per_minute = (values.speed / 60) * (WIDTH / 1000) * 100

        if values.automatic:

            # Calculate target valve percentage based on speed using (throughput * area_per_minute / throughput_max)
            # Where 100 is the conversion to percentage
            calculated_percentage = (values.target_throughput * ha_per_minute / CALIBRATION_VALUE) * 100

            # Max out at 100%
            if calculated_percentage > 100:
                calculated_percentage = 100

            if int(calculated_percentage) == int(values.target_valve_percentage):
                # Skip if we have same values
                return

            values.target_valve_percentage = calculated_percentage

        # Open valve to specific percentage
        set_ext_valve(values.target_valve_percentage)
        ws.send_to_vt(macro_commands.change_size_cmd(31, int(MAX_WIDTH_INDICATOR * values.target_valve_percentage / 100), 28))
    else:
        # Close valve
        set_ext_valve(0)
        ws.send_to_vt(macro_commands.change_size_cmd(31, 0, 28))


def set_ext_valve(percentage):
    """
    Set the external valve to a specific percentage
    """
    logging.debug("Setting external valve to %d%%", percentage)
    # controller.set_target(percentage)

from dataclasses import dataclass
import os
from main import Values
from make_pool_data import PreparedPoolData
from calculations import update_valve
import pyisolib.macro_commands as macro_commands
from pyisolib.functions import Activation
from pyisolib.pyisolib.vt_objects.object_pool import ObjectPool
from pyisolib.working_set import WorkingSet
import logging
import time
import j1939


logging.getLogger("j1939").setLevel(logging.DEBUG)
logging.getLogger("can").setLevel(logging.DEBUG)

# compose the name descriptor for the new ca
name = j1939.Name(
    arbitrary_address_capable=0,
    industry_group=j1939.Name.IndustryGroup.AgriculturalAndForestry,
    vehicle_system_instance=0,
    vehicle_system=1,
    function=4,
    function_instance=0,
    ecu_instance=0,
    manufacturer_code=111,
    identity_number=1234567,
)  # TODO: change parameters to your own values

ca = j1939.ControllerApplication(name, 128)

# create the ElectronicControlUnit (one ECU can hold multiple ControllerApplications)
ecu = j1939.ElectronicControlUnit()
ws = WorkingSet(ca)

# Below we create an instance of Values where we will keep track of the current state of the machine
values = Values()


def main():
    print("Initializing")

    # Start canbus communication with baudrate of 250kbps
    os.system("sudo ip link set can0 type can bitrate 250000")
    os.system("sudo ifconfig can0 up")
    os.system("sudo ifconfig can0 txqueuelen 1000")

    try:
        # Connect to the canbus
        ecu.connect(bustype="socketcan", channel="can0")
        ecu.add_ca(controller_application=ca)

        # Load the cached pool data file if present, otherwise create it.
        # See the README.md for more information on how to generate the pool data file AND when to update it
        POOL_DATA_FILE_NAME = "vtpooldata.bin"
        if os.path.isfile(POOL_DATA_FILE_NAME):
            ws.set_object_pool_file(POOL_DATA_FILE_NAME)
        else:
            pool_data = PreparedPoolData()
            ObjectPool.save_pooldata_to_file(pool_data, POOL_DATA_FILE_NAME)

        ca.start()
        print("Starting CA...")

        # Wait for controller apllication to be ready
        while ca.state != j1939.ControllerApplication.State.NORMAL:
            time.sleep(1)

        print("Starting WS...")
        ws.start()

        # Wait for the working set to operate normally (It must upload the objectpool etc.)
        while ws.state != WorkingSet.State.NORMAL:
            time.sleep(1)

        # Listen to functions now the workingset is started
        ws.add_listener(listen_functions, True)
        ws.add_listener(listen_canbus, False)
        print(
            f"""Specifications of VT: width {ws.technical_data.screen_width}, height {ws.technical_data.screen_height}, version {ws.technical_data.vt_version}, 
              physical_softkey_amount {ws.technical_data.soft_key_physical_amount}, virtual_softkey_amount {ws.technical_data.soft_key_virtual_amount}, 
              virtual_softkey_height {ws.technical_data.soft_key_height}, virtual_softkey_width {ws.technical_data.soft_key_width}"""
        )

        print("Listening to potmeter")
        while True:
            # Output of controller.run should be the percentage of the valve (measured)
            # values.current_valve_percentage = controller.run()

            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        print("Deinitializing")
        ca.stop()
        ecu.disconnect()
        os.system("sudo ifconfig can0 down")


def listen_canbus(pgn, data):
    if pgn == 65096:  # Ground based speed
        new_speed = (data[0] * 0.001 + data[1] * 0.256) * 3.65

        # Ignore if speed is still the same
        if new_speed == values.speed:
            return
        values.speed = new_speed

        # Send speed to display
        ws.send_to_vt(macro_commands.convert_numericvalue_cmd(302, int(values.speed * 10)))

        # Notify everything that valve size must be modified
        update_valve()

    elif pgn == 65091:  # PTO speed
        values.pto_speed = int(int.from_bytes(data[0:2], "little") * 0.125)
        ws.send_to_vt(macro_commands.convert_numericvalue_cmd(303, int(values.pto_speed)))


def listen_functions(function, data):
    if function == Activation.SOFT_KEY:
        code = data[0]
        if code != 0:  # If code is not key released we ignore
            return

        object_id = int.from_bytes(data[1:3], "little")
        if object_id == 1002 or object_id == 1003:  # Minus or plus throughtput button released

            if values.automatic:
                # We change the target throughtput if it's set to automatic
                if object_id == 1002:  # Minus
                    values.target_throughput = max(0, values.target_throughput - 10)  # Take 10 of the current target output but make sure it stays above 0
                else:  # Plus
                    values.target_throughput += 10  # Add 10
                ws.send_to_vt(macro_commands.convert_numericvalue_cmd(300, values.target_throughput))
            else:
                # We directly change the valve if it's set to manual
                values.target_valve_percentage += -5 if object_id == 1002 else 5
                values.target_valve_percentage = min(100, max(0, values.target_valve_percentage))  # Limit the percentage to 0-100%
                update_valve()  # Update the external valve

        elif object_id == 1100:  # Start button pressed
            assert values.running == False
            values.running = True
            update_valve()  # Update the external valve
            print("Running!")

        elif object_id == 1102:  # Stop button pressed
            assert values.running == True
            values.running = False
            update_valve()  # Update the external valve
            print("Stopped!")

        elif object_id == 1110:  # Manual button pressed
            assert values.automatic == True
            values.automatic = False
            ws.send_to_vt(macro_commands.convert_numericvalue_cmd(300, 0))  # Set the target flow seen by the user to 0
            print("Manual!")

        elif object_id == 1112:  # Automatic button pressed
            assert values.automatic == False
            values.automatic = True
            ws.send_to_vt(macro_commands.convert_numericvalue_cmd(300, values.target_throughput))  # Set the target flow to the previous target flow
            print("Auto!")


if __name__ == "__main__":
    main()

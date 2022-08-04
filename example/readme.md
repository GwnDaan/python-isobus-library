# Fertilizer Spreader Example

This folder of the repository demonstrates basic usage of the `pyisolib` package. It contains a simple example of a terminal for controlling a implement through ISOBUS' Universal Terminal (UT). Note that, since this example is for demonstration purposes, the logic (e.g. reading sensors, controlling motors) of the implement itself is left out. 

# Hardware

The parts used for this build are:
- Raspberry Pi Zero 2 W
- [CAN hat for Raspberry Pi](https://www.waveshare.com/rs485-can-hat.htm)

The Raspberry Pi is mounted on the Fertilizer spreader, and connected via the CAN hat to the canbus via the corrosponding connector on the back of the tractor. Note that there could be multiple connectors for ISOBUS in- and outside the cab of the tractor, so choose what is most convienent for you.

# Software

- `main.py`: This file contains the startup/shutdown logic and listens to messages send on the canbus.
- `calculations.py`: This part of the code holds the state of the implement locally and calculates the valve state when needed.
- `make_pool_data.py`: This script generates an object pool data file for the fertilizer spreader terminal. This file will later be transfered to the UT via the `WorkingSet` class in the `pyisolib` package. This step is not necessary, but as generating the object pool is quite an heavy operation for the RPI Zero, doing it this way recudes the load time of the implement by a lot.
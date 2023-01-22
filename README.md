## Python ISOBUS Library 

**Discontinued in favor of further development of [isobus++](https://github.com/ad3154/ISO11783-CAN-Stack). I plan to wrap it for Python when we release a stable version.**


This project is created to quickly setup a new 'virtual terminal' for an implement connected to a tractor using ISOBUS.
Get to know more about ISOBUS: [What is ISOBUS?](https://www.autopi.io/blog/what-is-isobus-and-iso11783/)

### Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes.

Requirements for the software and other tools to build, test and push 
- [Python 3.x](https://www.python.org/downloads/)
- CANbus -> serial peripheral (e.g. a [RPI-can-hat](https://www.waveshare.com/rs485-can-hat.htm))

Install pyisobus with pip:

    $ pip install git+https://github.com/GwnDaan/python-isobus-library.git#egg=pyisobus

### Quick Start

See the [example](https://github.com/GwnDaan/python-isobus-library/tree/master/example) on how to setup a virtual terminal yourself.

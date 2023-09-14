# PICO W based lock prototype v0

This directory contains hardware prototype schematic and software of SmartLock. It supports basic functionality 
of locking and unlocking doors with smartphone using Low Energy Bluetooth as communication medium. Main object of 
version 0 is to create hardware base for SmartLock, that can be extended and adjusted to your need by extending software
and adding new hardware.

## Software config
Software is written is micropython compiled for RP2040 microprocessor and used Pico W board settings. In this version of 
project (V0) we put low difficulty level on first place, which comes with cost of limited functionality. From both
limitations of Micropython itself as well, as reduced complexity of project.

## Hardware config 

### Required components (and estimated prices as of 2023)
* 1x [Raspberry Pico W](https://botland.store/raspberry-pi-pico-modules-and-kits/21575-raspberry-pi-pico-wh-rp2040-arm-cortex-m0-cyw43439-wifi-with-headers-5056561800196.html) ~9 EUR
* 1x [DC connector 5,5x2,1mm](https://botland.store/protoboard-connector-board-accessories/9419-module-with-dc-55x21mm-socket-led-5904422313296.html) ~1 EUR
* 1x [Power supply 5V/3A](https://botland.store/socket-power-supply/7160-power-supply-5v-3a-dc-55-21mm-5902135147627.html) ~6 EUR
* 1x [Breadboard + jumper wires](https://botland.store/breadoards/1504-set-of-breadboard-830-140-jumper-wires-5904422303556.html)* ~9 EUR

Estimated total price ~25 EUR.

Optional components marked with `*`

We used [Botland store](https://botland.store/)
as prices source, as it one of more known stores in Europe. You may find components more pricey depending on country you buy
them in. Always check if all components are in your budget before buying anything.

### Schema
[Schema file](Schem_SmartLock_PicoW_V0.json) was prepared with [EasyEDA Standard](https://easyeda.com/page/download) tool.

![V0 schema](Schematic_SmartLock_PicoW_V0.svg)

Schema uses only components listed above in section [Required components](#required-components-and-estimated-prices-as-of-2023).
There should not be need to use any other components, except solder, some screws and tools.

### Useful tools
* Universal multimeter
* Soldering station

## Building V0
TBA

## Extending V0
TBA

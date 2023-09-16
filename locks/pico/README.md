# PICO W based lock prototype v0

This directory contains hardware prototype schematic and software of SmartLock. It supports basic functionality 
of locking and unlocking doors with smartphone using Low Energy Bluetooth as communication medium. Main object of 
version 0 is to create hardware base for SmartLock, that can be extended and adjusted to your need by extending software
and adding new hardware.

Idea of SmartLock project is to extend existing physical security locks and make them more practical in modern day of
technology. And do it with freedom and transparency in mind. You don't need to believe proprietary solutions
anymore, when you can build your own lock, and review each part of its software, adjust it to your needs and even
distribute prebuild and/or modified solution of your own.

Currently project in version V0 supports:

* BLE interface for communication with [smartphone app](../../keys/phone)
* TBA

Refer to content of this document to learn how to build you own SmartLock.

## Software config
Software is written is micropython compiled for RP2040 microprocessor and used Pico W board settings. In this version of 
project (V0) we put low difficulty level on first place, which comes with cost of limited functionality. From both
limitations of Micropython itself as well, as reduced complexity of project.

### Source code

Source code is located in directory [src](src). It contains all necessary code to run you SmartLock V0, which should be
sufficient to run with hardware specified in section [Hardware config](#hardware-config) and connected as described in
section [Building V0](#building-v0). If you introduced any hardware changes, make sure, you adjusted source code
accordingly.

You can freely [clone](https://git-scm.com/docs/git-clone) or download this repository and introduce changes you want.
All software is licensed using [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0), which means it is
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, but you are free to use this software
as you want, introduce changes and redistribute it. You can find details in [LICENSE](../../LICENSE) file.

### Testing

If you are unfamiliar with concept of software testing, it is software version of "Measure twice, cut once".
To make sure our software works correctly and keep basic quality standards, as well as help you with introducing your
own
changes we prepared set of various tests, that simulate different use scenarios and evaluate software behaviour.
You can read more about software testing in [this article prepared by IBM](https://www.ibm.com/topics/software-testing).

Tests are located in directory [test](test) and created using unittest python framework. (Both its cpython and
micropython
versions). Tests are prepare to be able run on PC using standard [Python](https://www.python.org/) environment as well
as directly on Raspberry Pi Pico W using [Micropython](https://micropython.org/).

To run tests on PC you need to install Python in version at least 3.11 (Navigate to
section [Installing software](#installing-software)
to learn how install python environment and `mpremote` tool).

For testing on PC navigate to SmartLock for Pico directory (the same directory and this README file) and run command

```commandline
python3 -m unittest discover
```

It should result in output like

```commandline
Ran 1 test in 0.000s

OK
```

To run the same tests on you Pico you need to run command (using `mpremote` tool):

```commandline
python3 -m mpremote mount ./ exec "import test;" disconnect
```

This command assume that you have installed on Pico all necessary libraries, but if it not the case, you need to run
following command:

```commandline
python3 -m mpremote mip install fnmatch pathlib unittest
```

Please note that running test directly on Pico device will be much slower and will take considerate amount of time.

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

### Putting hardware together

### Installing software

To install software, you need to install micropython firmware as described
in [Raspberry Pi Pico documentation](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html).
After that, you simply need to copy source files (directory [src](src) content) directly to Pico root directory. For
example using `mpremote` command.

Installing `mpremote` on linux using `apt` package manager

```commandline
sudo apt install python3
python3 -m pip install mpremote
```

Using mpremote to install software on Pico

```commandline
python3 -m mpremote cp src/* :/ +
python3 -m mpremote reset
```

### Troubleshooting

Sometimes you may stumble upon some problems with executing mpremote commands. Refer to this section for most common
problems.

#### Error `no device found` on Linux

The most common reason is that you didn't connect you RPI Pico correctly to your PC or you have incorrectly set
permissions.
We suggest following
official [Raspberry Pi Pico guide](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf)
to learn how to connect and test your Pico.

But if you want some quick tips:

* You can check if you Linux system detects properly you Pico by running `ls /dev/tty*` command. You should see device
  like
  `ttyACM0`, `ttyUSB0` or something similar. If there is no such device, it most likely problem you your USB port, OS
  drivers
  Pico not having installed correct firmware, or you are using WSL2, which have [known problem](#no-pico-device-on-wsl2)
* If you can see Pico tty device, check if you have correct access rights and your account belong to correct group on
  linux.
  You can use command `stats` to check it.
* Pico may be in bootloader mode, which make it to be visible as usb drive, not serial device. You may need simply to
  reconnect
  Pico (or install correct firmware).
* It is worth to reinstall your Pico firmware using correct firmware version, if you have troubles with it. It is
  possible
  that you installed incorrect version by mistake.

#### No Pico device on WSL2

It is known for years ~~bug~~ lack of feature on WSL2, which probably will not be fixed in close future.
Fortunately it has verified [workaround](https://devblogs.microsoft.com/commandline/connecting-usb-devices-to-wsl/),
which works well for this project.

#### Pico seems to not have BLE interface (`ImportError: no module named 'bluetooth'`, `ImportError: can't import name BLE1`, `AttributeError: 'module' object has no attribute 'BLE'`)

Make sure you have Pico in version W. Normal Pico do not come with WiFi and BLE modules. Only W variance have these
capabilities.

If you have correct Pico version, make sure you installed correct firmware version dedicated for Pico W. Firmware for
normal Pico do not have support for wireless capabilities.

## Extending V0
TBA

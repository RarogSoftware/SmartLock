# ------------------------------------------------------------------------------
#  Copyright (c) 2023 onwards, Pawel Przytarski                                -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

import time

import machine
from micropython import const

from .generic import RTC

DS1307_ADDRESS = const(0x68)
DS1307_CONTROL_ADDRESS = const(0x07)
DS1307_WAVE_CONTROL_BIT = const(0b10000)


class DS1307(RTC):
    def __init__(self,
                 sda_pin: int = 20,
                 scl_pin: int = 21,
                 irq_pin: int | None = 22,
                 enable_irq: bool = False,
                 irq_freq: int = 1
                 ):
        """
        Initializes DS1307 device connection using I2C bus

        :param sda_pin: SDA on device connected with SDA pin on DS1307
        :param scl_pin: SCL on device connected with SDA pin on DS1307
        :param irq_pin: Pin on device which is connected to SQ pin on DS1307. It will be used for irq
        :param enable_irq: initial state Square Wave on DS1307, which is used for IRQ on device
        :param irq_freq: initial frequency of Square Wave
        """

        self._i2c: machine.I2C = machine.SoftI2C(machine.Pin(scl_pin),
                                                 machine.Pin(sda_pin),
                                                 freq=400_000
                                                 )
        if irq_pin is not None:
            self._irq_pin = machine.Pin(irq_pin, mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
        else:
            self._irq_pin = None

        scan_result = self._i2c.scan()

        self._setIrqConfig(enable_irq, irq_freq)

        if DS1307_ADDRESS not in scan_result:
            raise ConnectionError("DS1307 not connected to I2C")

    def _setIrqConfig(self, enable_irq, irq_freq):
        value = 0 | (DS1307_WAVE_CONTROL_BIT if enable_irq else 0) \
                | self._getFrequencyBits(irq_freq)

        self._i2c.writeto_mem(DS1307_ADDRESS, DS1307_CONTROL_ADDRESS, bytearray([value]))

    def getUnixTime(self) -> int:
        return time.mktime(self.getTime())

    def getTime(self):
        self._i2c.start()
        data = self._i2c.readfrom_mem(DS1307_ADDRESS, 0x00, 7)
        self._i2c.stop()
        return (
            self._decodeBCD(data[6]) + 2000,
            self._decodeBCD(data[5] & 0x3F),
            self._decodeBCD(data[4] & 0x3F),
            self._decodeHour(data[2]),
            self._decodeBCD(data[1]),
            self._decodeBCD(data[0] & 0x7F),
            self._decodeBCD(data[3] & 0x07),
            -1
        )

    def setUnixTime(self, seconds: int):
        self.setTime(time.gmtime(seconds))

    def setTime(self, date):
        (year, month, day, hour, minute, second, weekday, *_) = date
        self._i2c.writeto_mem(DS1307_ADDRESS, 0x00, bytearray([
            self._encodeBCD(second),
            self._encodeBCD(minute),
            self._encodeBCD(hour),
            self._encodeBCD(weekday),
            self._encodeBCD(day),
            self._encodeBCD(month),
            self._encodeBCD(year - 2000),
        ]))
        self._i2c.stop()

    def enableIrq(self):
        self._checkIrqPin()
        self.enableIrqOnDevice()

    def enableIrqOnDevice(self):
        self._i2c.start()
        data = self._i2c.readfrom_mem(DS1307_ADDRESS, DS1307_CONTROL_ADDRESS, 1)
        value = data[0] | DS1307_WAVE_CONTROL_BIT
        self._i2c.writeto_mem(DS1307_ADDRESS, DS1307_CONTROL_ADDRESS, bytearray([value]))
        self._i2c.stop()

    def _checkIrqPin(self):
        if self._irq_pin is None:
            raise ValueError('Cannot change IRQ settings because there is no IRQ pin configured')

    def disableIrq(self):
        self._checkIrqPin()
        self.disableIrqOnDevice()

    def disableIrqOnDevice(self):
        self._i2c.start()
        data = self._i2c.readfrom_mem(DS1307_ADDRESS, DS1307_CONTROL_ADDRESS, 1)
        value = data[0] & (DS1307_WAVE_CONTROL_BIT ^ 0xFF)
        self._i2c.writeto_mem(DS1307_ADDRESS, DS1307_CONTROL_ADDRESS, bytearray([value]))
        self._i2c.stop()

    def getAvailableIrqFrequencies(self) -> list[int]:
        return [1, 4_096, 8_192, 32_768]

    def setIrqFrequency(self, value: int):
        bits = self._getFrequencyBits(value)
        self._i2c.start()
        data = self._i2c.readfrom_mem(DS1307_ADDRESS, DS1307_CONTROL_ADDRESS, 1)
        value = data[0] & 0xFC | bits
        self._i2c.writeto_mem(DS1307_ADDRESS, DS1307_CONTROL_ADDRESS, bytearray([value]))
        self._i2c.stop()

    def irq(self, handler=None, **kwargs):
        self._checkIrqPin()
        self._irq_pin.irq(handler, trigger=machine.Pin.IRQ_RISING, **kwargs)

    @staticmethod
    def _decodeBCD(val):
        return ((val >> 4) * 10) + (val & 0xF)

    @staticmethod
    def _encodeBCD(val):
        return (val % 10) + (val // 10 << 4)

    @staticmethod
    def _decodeHour(val):
        if val >> 6 & 1 == 1:
            # AM/PM mode
            ampm = val >> 5 & 1
            hour = (val & 0xf) + (val >> 4 & 1)
            if hour == 1 and ampm == 1:
                return 0
            else:
                return hour + ampm * 12
        else:
            # 24 mode
            return DS1307._decodeBCD(val & 0x3F)

    @staticmethod
    def _getFrequencyBits(irq_freq):
        if irq_freq == 1:
            return 0b00
        elif irq_freq == 4_096:
            return 0b01
        elif irq_freq == 8_192:
            return 0b10
        elif irq_freq == 32_768:
            return 0b11
        else:
            raise ValueError("Frequency outside of acceptable values")

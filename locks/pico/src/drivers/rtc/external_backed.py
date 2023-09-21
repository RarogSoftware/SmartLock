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

from .ds1307 import DS1307
from .generic import RTC

DS1307_ADDRESS = const(0x68)
DS1307_CONTROL_ADDRESS = const(0x07)
DS1307_WAVE_CONTROL_BIT = const(0b10000)


class ExternalBackedRtc(RTC):
    def __init__(self,
                 delegate: RTC = None
                 ):
        if delegate is None:
            delegate = DS1307()

        self._rtc = machine.RTC()
        self._delegate = delegate

        (year, month, day, hour, minute, second, weekday, *_) = delegate.getTime()
        self._rtc.datetime((year, month, day, weekday, hour, minute, second, 0))

    def getUnixTime(self) -> int:
        return time.mktime(self.getTime())

    def getTime(self):
        (year, month, day, weekday, hour, minute, second, *_) = self._rtc.datetime()
        return (year, month, day, hour, minute, second, weekday, -1)

    def setUnixTime(self, seconds: int):
        self.setTime(time.gmtime(seconds))

    def setTime(self, datetime):
        (year, month, day, hour, minute, second, weekday, *_) = datetime
        self._rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
        self._delegate.setTime(datetime)

    def enableIrq(self):
        self._delegate.enableIrq()

    def disableIrq(self):
        self._delegate.disableIrq()

    def getAvailableIrqFrequencies(self) -> list[int]:
        return self._delegate.getAvailableIrqFrequencies()

    def setIrqFrequency(self, value: int):
        self._delegate.setIrqFrequency(value)

    def irq(self, handler=None, **kwargs):
        self._delegate.irq(handler, **kwargs)

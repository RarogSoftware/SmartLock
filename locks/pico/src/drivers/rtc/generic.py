# ------------------------------------------------------------------------------
#  Copyright (c) 2023 onwards, Pawel Przytarski                                -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

import time


class RTC:
    def getUnixTime(self) -> int:
        return time.time()

    def getTime(self):
        return time.localtime(self.getUnixTime())

    def setUnixTime(self, seconds: int):
        (year, month, day, hour, minute, second, weekday, *_) = time.localtime(seconds)
        self.setTime((year, month, day, hour, minute, second, weekday))

    def setTime(self, datetime):
        raise NotImplemented()

    def enableIrq(self):
        raise NotImplemented()

    def disableIrq(self):
        raise NotImplemented()

    def getAvailableIrqFrequencies(self) -> list[int]:
        raise NotImplemented()

    def setIrqFrequency(self, value: int):
        raise NotImplemented()

    def irq(self, handler=None, **kwargs):
        raise NotImplemented()

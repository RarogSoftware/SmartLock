# ------------------------------------------------------------------------------
#  Copyright (c) 2023 onwards, Pawel Przytarski                                -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

from drivers.rtc.generic import RTC


class Clock:
    def __init__(self, rtc: RTC = None):
        if rtc is None:
            from drivers.rtc.external_backed import ExternalBackedRtc
            from drivers.rtc.ds1307 import DS1307
            self._rtc = ExternalBackedRtc(DS1307())
        else:
            self._rtc = rtc

    def getTime(self):
        return self._rtc.getTime()

    def getIsoTime(self):
        (year, month, day, hour, minute, second, *_) = self._rtc.getTime()
        return f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}+00:00"

    def getUnixTime(self):
        return self._rtc.getUnixTime()

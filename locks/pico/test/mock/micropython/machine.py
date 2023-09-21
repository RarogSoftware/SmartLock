# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
import time


class RTC:
    def __init__(self):
        self._offset = 0

    def datetime(self, datetime=None):
        if datetime is not None:
            (year, month, day, weekday, hour, minute, second, *_) = datetime
            unix = time.mktime((year, month, day, hour, minute, second, weekday, -1, 0))
            self._offset = time.mktime(time.localtime()) - unix
        (year, month, day, hour, minute, second, weekday, *_) = time.localtime(
            time.mktime(time.localtime()) - self._offset)
        return (year, month, day, weekday, hour, minute, second, 0)

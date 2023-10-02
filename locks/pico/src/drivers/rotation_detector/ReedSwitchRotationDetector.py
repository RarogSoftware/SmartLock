# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
import time

from machine import Pin

from .rotation_detector import RotationDetector
from ..helpers import PinLike, PinHelpers


class SingleDirectionReedSwitchDetector(RotationDetector):
    def __init__(self,
                 pin: PinLike,
                 numberOfSwitchesPerRotation=1,
                 debounceMs=100):
        self._lpin = PinHelpers.pinLikeToInPin(pin, "pin", Pin.PULL_UP)
        self._degreesChange = 360.0 / numberOfSwitchesPerRotation
        self._debounce = debounceMs
        self._lastDetection = time.ticks_ms()
        super().__init__()

    def init(self):
        self._lpin.init(Pin.IN, Pin.PULL_UP)
        self._lpin.irq(self._irq, trigger=Pin.IRQ_FALLING)
        self._lastDetection = time.ticks_ms()

    def _irq(self, pin):
        prev = self._lastDetection
        self._lastDetection = time.ticks_ms()
        if self._lastDetection - prev > self._debounce:
            self._updateDegrees(self._degreesChange)

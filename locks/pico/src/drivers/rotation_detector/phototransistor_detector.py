# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

from machine import ADC, Timer

from .rotation_detector import *

ADC_MAX_VALUE = const(55000.0)
ADC_HIGH_VALUE = const(45000.0)
ADC_LOW_VALUE = const(10000)
STEPS_COUNT = const(18)


class SteppingPhotoTransistorRotationDetector(RotationDetector):
    def __init__(self,
                 pin: ADC):
        if pin is None or not isinstance(pin, ADC):
            raise ValueError("Pin must be valid ADC pin")
        self._pin = pin
        self._degreesChange = 360.0 / STEPS_COUNT
        self._previous = None
        self._timer = Timer()
        super().__init__()

    def init(self):
        self._timer.init(mode=Timer.PERIODIC, period=5, callback=self._irq)
        self._previous = None

    def getCurrentRotations(self) -> float:
        return super().getCurrentRotations()

    @staticmethod
    def _abs(value):
        if value < 0:
            return - value
        return value

    def _irq(self, timer):
        if self._previous is None:
            self._previous = 1 if self._pin.read_u16() > ADC_HIGH_VALUE else 0
        else:
            value = self._pin.read_u16()
            if value > ADC_HIGH_VALUE and self._previous == 0:
                self._updateDegrees(self._degreesChange)
                self._previous = 1
            elif value < ADC_LOW_VALUE and self._previous == 1:
                self._previous = 0

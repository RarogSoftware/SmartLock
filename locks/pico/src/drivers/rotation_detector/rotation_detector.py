# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
from micropython import const

TRIGGER_ROTATION_CHANGE = const(0b1)
TRIGGER_FULL_ROTATION = const(0b10)


class RotationDetector:
    def __init__(self):
        self._degrees = 0.0
        self._irqHandler = None
        self._irqTrigger = 0
        self._direction = 1
        self.init()

    def init(self):
        self.resetCurrentDegree()

    def getCurrentDegree(self) -> float:
        return self._degrees

    def getCurrentRotations(self) -> float:
        return self._degrees / 360.0

    def irq(self, handler, trigger: int = TRIGGER_ROTATION_CHANGE) -> None:
        self._irqHandler = handler
        self._irqTrigger = trigger

    def resetCurrentDegree(self) -> None:
        self.setCurrentDegree(0)

    def setCurrentDegree(self, value) -> None:
        self._degrees = value

    def setDirection(self, direction):
        self._direction = direction

    def _updateDegrees(self, value: float):
        prevRotations = self.getCurrentRotations()
        self._degrees = self._degrees + value * self._direction
        currentRotations = self.getCurrentRotations()
        if self._irqTrigger & TRIGGER_ROTATION_CHANGE != 0:
            self._irqHandler(TRIGGER_ROTATION_CHANGE, self._degrees)
        if self._irqTrigger & TRIGGER_FULL_ROTATION != 0 and prevRotations != currentRotations:
            self._irqHandler(TRIGGER_FULL_ROTATION, currentRotations)

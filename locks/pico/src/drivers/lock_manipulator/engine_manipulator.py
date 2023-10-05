# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

from .startstop_manipulator import *
from ..helpers import PinLike, PinHelpers
from ..rotation_detector.rotation_detector import RotationDetector


class EngineLockManipulator(StartStopLockManipulator):
    def __init__(self,
                 clockwisePin: PinLike = 16,
                 counterClockwisePin: PinLike = 17,
                 rotationDetector: RotationDetector = None):
        super().__init__(rotationDetector)
        self._clockwise = PinHelpers.pinLikeToOutPin(clockwisePin, "clockwisePin")
        self._counterclockwise = PinHelpers.pinLikeToOutPin(counterClockwisePin, "counterClockwisePin")

    async def init(self, fullLockRotations: int = 2, initialState: int = LOCK_UNINITIALIZED,
                   lockDirection: int = LOCK_DIRECTION_COUNTERCLOCKWISE) -> None:
        self._clockwise.init(Pin.OUT)
        self._counterclockwise.init(Pin.OUT)
        await super().init(fullLockRotations, initialState, lockDirection)

    def _detectHardwareStalled(self):
        return False

    def _rotateCounterClockwise(self):
        self._clockwise.off()
        time.sleep_ms(1)  # prevent shortcutting circuit
        self._counterclockwise.on()

    def _rotateClockwise(self):
        self._counterclockwise.off()
        time.sleep_ms(1)  # prevent shortcutting circuit
        self._clockwise.on()

    def _stopLock(self):
        self._counterclockwise.off()
        self._clockwise.off()

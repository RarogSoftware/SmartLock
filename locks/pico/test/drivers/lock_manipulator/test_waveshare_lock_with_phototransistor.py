# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
import asyncio
import unittest

from machine import UART, ADC

import test.conditions
from src.drivers.lock_manipulator.lock_manipulator import *
from src.drivers.lock_manipulator.wavesharesc_servo_manipulator import WaveshareScServoLockManipulator
from src.drivers.rotation_detector.phototransistor_detector import SteppingPhotoTransistorRotationDetector


@test.conditions.device_only()
@test.conditions.slow()
class TestWaveshareSCLockManipulatorWithPhotoTransistor(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        uart = UART(0, 1_000_000)
        uart.init(1_000_000, bits=8, parity=None, invert=0, stop=1, tx=16, rx=17)
        uart.read()
        adc = ADC(28)
        detector = SteppingPhotoTransistorRotationDetector(adc)
        self.lock = WaveshareScServoLockManipulator(uart,
                                                    rotationDetector=detector,
                                                    reedSwitchPin=13)
        self.uart = uart

    def tearDown(self) -> None:
        self.loop.run_until_complete(self.lock._stopLock())

    def testLockCanOperateClockwise(self):
        states = []
        errors = []

        def callback(state, error, lock):
            states.append(state)
            errors.append(error)

        self.lock.lockStateChangeCallback(callback=callback)

        self.loop.run_until_complete(self.lock.init(fullLockRotations=3, lockDirection=LOCK_DIRECTION_CLOCKWISE))

        self.assertLockWorks(states)

    def assertLockWorks(self, states):
        self.assertEqual(self.lock.getLockError(), None)
        self.assertEqual(self.lock.getLockState(), LOCK_WORKING_UNLOCKING)
        self.assertEqual(len(states), 3)
        self.loop.run_until_complete(self.lock._task)
        self.assertEqual(self.lock.getLockState(), LOCK_UNLOCKED)
        self.assertEqual(len(states), 4)
        self.loop.run_until_complete(self.lock.lock())
        self.loop.run_until_complete(self.lock.lock())
        self.loop.run_until_complete(self.lock.lock())
        self.assertEqual(self.lock.getLockState(), LOCK_WORKING_LOCKING)
        self.assertEqual(len(states), 5)
        self.loop.run_until_complete(self.lock._task)
        self.assertEqual(self.lock.getLockState(), LOCK_LOCKED)
        self.assertEqual(len(states), 6)
        self.loop.run_until_complete(self.lock.unlock())
        self.loop.run_until_complete(self.lock.unlock())
        self.loop.run_until_complete(self.lock.unlock())
        self.assertEqual(self.lock.getLockState(), LOCK_WORKING_UNLOCKING)
        self.assertEqual(len(states), 7)
        self.loop.run_until_complete(self.lock._task)
        self.assertEqual(self.lock.getLockState(), LOCK_UNLOCKED)
        self.assertEqual(len(states), 8)
        self.loop.run_until_complete(self.lock.unlock())
        self.loop.run_until_complete(self.lock.unlock())
        self.loop.run_until_complete(self.lock.lock())
        self.assertEqual(self.lock.getLockState(), LOCK_WORKING_LOCKING)
        self.assertEqual(len(states), 9)
        self.loop.run_until_complete(self.lock._task)
        self.assertEqual(self.lock.getLockState(), LOCK_LOCKED)
        self.assertEqual(len(states), 10)

    def testLockCanOperateCounterClockwise(self):
        states = []
        errors = []

        def callback(state, error, lock):
            states.append(state)
            errors.append(error)

        self.lock.lockStateChangeCallback(callback=callback)

        self.loop.run_until_complete(self.lock.init(fullLockRotations=3, lockDirection=LOCK_DIRECTION_COUNTERCLOCKWISE))

        self.assertLockWorks(states)

    def testLockCanOperateWith2Rotations(self):
        states = []
        errors = []

        def callback(state, error, lock):
            states.append(state)
            errors.append(error)

        self.lock.lockStateChangeCallback(callback=callback)

        self.loop.run_until_complete(self.lock.init(fullLockRotations=2, lockDirection=LOCK_DIRECTION_COUNTERCLOCKWISE))

        self.assertLockWorks(states)

    def testLockCanOperateWith5Rotations(self):
        states = []
        errors = []

        def callback(state, error, lock):
            states.append(state)
            errors.append(error)

        self.lock.lockStateChangeCallback(callback=callback)

        self.loop.run_until_complete(self.lock.init(fullLockRotations=5, lockDirection=LOCK_DIRECTION_COUNTERCLOCKWISE))

        self.assertLockWorks(states)

    def testLockCanOperateWith1Rotation(self):
        states = []
        errors = []

        def callback(state, error, lock):
            states.append(state)
            errors.append(error)

        self.lock.lockStateChangeCallback(callback=callback)

        self.loop.run_until_complete(self.lock.init(fullLockRotations=1, lockDirection=LOCK_DIRECTION_COUNTERCLOCKWISE))

        self.assertLockWorks(states)

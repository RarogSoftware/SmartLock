# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
import asyncio
import time

from machine import Pin

from .lock_manipulator import *
from ..helpers import PinLike, PinHelpers
from ..rotation_detector.rotation_detector import RotationDetector

LOCK_STOPPING_TIME = const(1.5)

MOVE_DETECTION_TIMEOUT = const(2500)


class StartStopLockManipulator(LockManipulator):
    def __init__(self,
                 rotationDetector: RotationDetector,
                 reedSwitchPin: PinLike):
        self._moveDetected = None
        self._detector = rotationDetector
        self._lock = asyncio.Lock()
        self._waitingLock = None
        self._task = None
        self._lastPosition = None
        self._positionZeroPin = PinHelpers.pinLikeToInPin(reedSwitchPin, "reedSwitchPin", pull=Pin.PULL_UP)
        super().__init__()

    async def init(self, fullLockRotations: int = 2, initialState: int = LOCK_UNINITIALIZED,
                   lockDirection: int = LOCK_DIRECTION_COUNTERCLOCKWISE) -> None:
        await self._lock.acquire()
        try:
            self._detector.init()
            if self._task:
                self._task.cancel()
            self._task = None
            self._lastPosition = None
            await super().init(fullLockRotations, initialState, lockDirection)
        finally:
            self._lock.release()

    async def lockState(self) -> int:
        await self._lock.acquire()
        try:
            return await super().lockState()
        finally:
            self._lock.release()

    async def lockError(self) -> int:
        await self._lock.acquire()
        try:
            return await super().lockError()
        finally:
            self._lock.release()

    async def unlock(self):
        await self._lock.acquire()
        try:
            if self._state == LOCK_ERROR:
                raise RuntimeError("Lock error")
            if self._state == LOCK_UNLOCKED \
                    or self._state == LOCK_WORKING_UNLOCKING:
                return
            await self._innerUnlock()
        finally:
            self._lock.release()

    async def _innerUnlock(self):
        self._state = LOCK_WORKING_UNLOCKING
        await self._callStateCallback()
        await self._rotateToUnlock()
        if self._task is None:
            self._task = asyncio.create_task(self._rotationTask())

    async def _rotateToUnlock(self):
        if self._direction == LOCK_DIRECTION_COUNTERCLOCKWISE:
            self._detector.setDirection(1)
            await self._rotateClockwise()
        else:
            self._detector.setDirection(-1)
            await self._rotateCounterClockwise()

    async def lock(self):
        await self._lock.acquire()
        try:
            if self._state == LOCK_ERROR:
                raise RuntimeError("Lock error")
            if self._state == LOCK_LOCKED \
                    or self._state == LOCK_WORKING_LOCKING:
                return
            self._state = LOCK_WORKING_LOCKING
            await self._callStateCallback()
            await self._rotateToLock()
            if self._task is None:
                self._task = asyncio.create_task(self._rotationTask())
        finally:
            self._lock.release()

    async def _rotateToLock(self):
        if self._direction == LOCK_DIRECTION_COUNTERCLOCKWISE:
            self._detector.setDirection(-1)
            await self._rotateCounterClockwise()
        else:
            self._detector.setDirection(1)
            await self._rotateClockwise()

    async def _rotationTask(self):
        await self._updateLastPositionChange()
        while True:
            await asyncio.sleep(0.01)

            if (await self._detectHardwareStalled()
                    or await self._detectNotMoving()):
                await self._markError(LOCK_ERROR_STALLED)
                break

            if self._lastPosition == self._detector.getCurrentRotations():
                continue

            if self._abs(self._lastPosition) > self._targetRotations + 0.7:
                await self._markError(LOCK_ERROR_OUTSIDE_OF_BOUNDS)
                break

            await self._updateLastPositionChange()

            await self._lock.acquire()
            try:
                if self._lastPosition == 0 and self._state == LOCK_WORKING_LOCKING:
                    await self._markFinished(LOCK_LOCKED)
                    break
                if self._state == LOCK_WORKING_UNLOCKING and self._abs(self._lastPosition) >= self._targetRotations:
                    await self._markFinished(LOCK_UNLOCKED)
                    break
            finally:
                self._lock.release()

    async def _updateLastPositionChange(self):
        self._moveDetected = time.ticks_ms()
        self._lastPosition = self._detector.getCurrentRotations()

    async def _markFinished(self, newState):
        await self._stopLock()
        await self._recenterLock(newState == LOCK_LOCKED)
        self._state = newState
        self._task = None
        await self._callStateCallback()

    async def _markError(self, error):
        await self._lock.acquire()
        try:
            await self._stopLock()
            self._state = LOCK_ERROR
            self._error = (0 if self._error is None else self._error) | error
            self._task = None
            await self._callStateCallback()
        finally:
            self._lock.release()

    async def _detectNotMoving(self):
        return self._moveDetected + MOVE_DETECTION_TIMEOUT < time.ticks_ms()

    @staticmethod
    def _abs(value):
        if value < 0:
            return -value
        return value

    async def _detectHardwareStalled(self):
        ...

    async def _rotateCounterClockwise(self):
        ...

    async def _rotateClockwise(self):
        ...

    async def _stopLock(self):
        ...

    async def determineState(self):
        await super().determineState()
        self._detector.resetCurrentDegree()

        await self._updateLastPositionChange()

        await self._rotateToLock()
        while self._abs(self._detector.getCurrentRotations()) < self._targetRotations \
                and not (await self._detectHardwareStalled() or await self._detectNotMoving()):
            await asyncio.sleep(0.005)
            if self._lastPosition != self._detector.getCurrentRotations():
                await self._updateLastPositionChange()
        await self._stopLock()

        await asyncio.sleep(LOCK_STOPPING_TIME)  # give time to fully stop
        madeRotations = self._abs(self._detector.getCurrentRotations())

        self._detector.resetCurrentDegree()
        await self._rotateToUnlock()
        while self._abs(self._detector.getCurrentRotations()) < 1 \
                and not (await self._detectHardwareStalled() or await self._detectNotMoving()) \
                and self._positionZeroPin.value() == 1:
            await asyncio.sleep(0.005)
            if self._lastPosition != self._detector.getCurrentRotations():
                await self._updateLastPositionChange()

        await self._stopLock()
        if self._abs(self._detector.getCurrentRotations()) > 1:
            raise RuntimeError("Cannot find neutral position of lock")

        await self._recenterLock(False)

        self._state = LOCK_LOCKED
        self._detector.resetCurrentDegree()
        await self._callStateCallback()

        if madeRotations >= self._targetRotations - 0.5:
            await self._innerUnlock()

    async def _recenterLock(self, forLocking):
        await asyncio.sleep(LOCK_STOPPING_TIME)
        toggle = -1 if forLocking else 1
        while self._positionZeroPin.value() == 1:
            toggle = toggle * -1
            if toggle == -1:
                await self._rotateToLock()
            else:
                await self._rotateToUnlock()
            while self._positionZeroPin.value() == 1:
                await asyncio.sleep(0.001)
            await self._stopLock()
            await asyncio.sleep(LOCK_STOPPING_TIME)
        await self._stopLock()

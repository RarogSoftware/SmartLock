# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

from micropython import const

LOCK_UNINITIALIZED = const(0)
LOCK_LOCKED = const(1)
LOCK_UNLOCKED = const(2)
LOCK_WORKING_LOCKING = const(3)
LOCK_WORKING_UNLOCKING = const(4)
LOCK_ERROR = const(100)

LOCK_ERROR_STALLED = const(1)
LOCK_ERROR_OUTSIDE_OF_BOUNDS = const(2)
LOCK_ERROR_HARDWARE_FAILURE = const(4)

LOCK_DIRECTION_COUNTERCLOCKWISE = const(-1)
LOCK_DIRECTION_CLOCKWISE = const(1)


class LockManipulator:
    def __init__(self):
        self._targetRotations = None
        self._direction = None
        self._state = None
        self._error = None
        self._stateChangeCallback = None

    async def init(self,
                   fullLockRotations: int = 2,
                   initialState: int = LOCK_UNINITIALIZED,
                   lockDirection: int = LOCK_DIRECTION_COUNTERCLOCKWISE) -> None:
        if fullLockRotations < 1 or fullLockRotations > 10:
            raise ValueError("fullLockRotations must be between 1 and 10")
        if initialState < LOCK_UNINITIALIZED or initialState >= LOCK_WORKING_LOCKING:
            raise ValueError("state must be LOCK_UNINITIALIZED, LOCK_LOCKED or LOCK_UNLOCKED")
        if lockDirection != LOCK_DIRECTION_COUNTERCLOCKWISE and lockDirection != LOCK_DIRECTION_CLOCKWISE:
            raise ValueError("lockDirection must be LOCK_DIRECTION_COUNTERCLOCKWISE or LOCK_DIRECTION_CLOCKWISE")

        self._direction = lockDirection
        self._state = initialState
        self._targetRotations = fullLockRotations
        if initialState == LOCK_UNINITIALIZED:
            await self._callStateCallback()
            await self.determineState()

    def lockStateChangeCallback(self, callback):
        self._stateChangeCallback = callback

    async def _callStateCallback(self):
        if self._stateChangeCallback is not None:
            self._stateChangeCallback(self._state, self._error, self)

    def getLockState(self) -> int:
        return self._state

    def getLockError(self) -> int:
        return self._error

    async def lockState(self) -> int:
        return self._state

    async def lockError(self) -> int:
        return self._error

    async def unlock(self) -> None:
        ...

    async def lock(self) -> None:
        ...

    async def determineState(self):
        ...

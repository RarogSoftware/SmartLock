# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
import struct

from machine import UART

from .startstop_manipulator import *

PING_INSTRUCTION = const(0x01)
READ_INSTRUCTION = const(0x02)
WRITE_INSTRUCTION = const(0x03)

MOTOR_MODE_MEMORY_ADDR = const(9)
TIME_MEMORY_ADDR = const(44)

SERVO_ID = const(1)


class WaveshareScServoLockManipulator(StartStopLockManipulator):
    def __init__(self,
                 communication: UART,
                 rotationDetector: RotationDetector,
                 reedSwitchPin: PinLike):
        super().__init__(rotationDetector, reedSwitchPin)
        self.uart = communication

    @staticmethod
    def controlSum(data):
        sum = 0
        for arg in data:
            sum = sum + arg
        return (~sum) & 0xff

    @staticmethod
    def message(data):
        buf = [0xFF, 0xFF]
        for arg in data:
            buf.append(arg)
        buf.append(WaveshareScServoLockManipulator.controlSum(data))
        return buf

    def writeMessage(self, instruction, parameters=None):
        if parameters is None:
            parameters = []
        length = 2 + len(parameters)
        buffer = [SERVO_ID, length, instruction]
        buffer = bytearray(self.message(buffer + parameters))
        self.uart.read()
        self.uart.write(buffer)
        self.uart.flush()
        time.sleep_us(1)
        self.uart.read(len(buffer))

    def readMessage(self, timeout=10):
        endTime = time.ticks_ms() + timeout
        while endTime > time.ticks_ms():
            buff = self.uart.read(100)
            if buff is None:
                time.sleep_us(10)
                continue
            for i in range(0, len(buff) - 5):
                if buff[i] != 0xff or buff[i + 1] != 0xff:
                    continue
                if buff[i + 2] != SERVO_ID:
                    self.uart.read()
                    return [], 0xff
                (length, error) = struct.unpack_from(">BB", buff, i + 3)
                checksum = self.uart.read(i + 3 + length)
                buff = buff[i + 5:i + 3 + length]
                calculatedChecksum = self.controlSum([SERVO_ID, length, error] + list(buff))
                if checksum != calculatedChecksum:
                    return buff, error & 0b10
                return buff, error
        return [], 0xff

    async def init(self, fullLockRotations: int = 2, initialState: int = LOCK_UNINITIALIZED,
                   lockDirection: int = LOCK_DIRECTION_COUNTERCLOCKWISE) -> None:
        self.writeMessage(PING_INSTRUCTION, [])
        time.sleep_ms(1)
        buff, error = self.readMessage()
        if error != 0:
            await self._markError(LOCK_ERROR_HARDWARE_FAILURE)
            raise RuntimeError("Servo do not respond")
        self.writeMessage(WRITE_INSTRUCTION, [MOTOR_MODE_MEMORY_ADDR, 0, 0, 0, 0])
        time.sleep_ms(1)
        buff, error = self.readMessage()
        if error != 0:
            await self._markError(LOCK_ERROR_HARDWARE_FAILURE)
            raise RuntimeError("Servo is broken. Cannot operate.")

        await super().init(fullLockRotations, initialState, lockDirection)

    async def _detectHardwareStalled(self):
        self.writeMessage(READ_INSTRUCTION, [66, 1])
        buff, error = self.readMessage()
        return error != 0

    async def _rotateCounterClockwise(self):
        self.writeMessage(WRITE_INSTRUCTION, [TIME_MEMORY_ADDR, 40, 0])
        buff, error = self.readMessage()
        if error != 0:
            await self._markError(LOCK_ERROR_HARDWARE_FAILURE)
            raise RuntimeError("Servo is broken. Cannot operate.")

    async def _rotateClockwise(self):
        self.writeMessage(WRITE_INSTRUCTION, [TIME_MEMORY_ADDR, 240, 0])
        buff, error = self.readMessage()
        if error != 0:
            await self._markError(LOCK_ERROR_HARDWARE_FAILURE)
            raise RuntimeError("Servo is broken. Cannot operate.")

    async def _stopLock(self):
        i = 0
        while i < 10:  # really hard try to stop lock
            i = i + 1
            try:
                self.writeMessage(WRITE_INSTRUCTION, [TIME_MEMORY_ADDR, 0, 0])
                break
            except Exception:
                time.sleep_ms(1)
        buff, error = self.readMessage()
        if error != 0:
            await self._markError(LOCK_ERROR_HARDWARE_FAILURE)
            raise RuntimeError("Servo is broken. Cannot operate.")

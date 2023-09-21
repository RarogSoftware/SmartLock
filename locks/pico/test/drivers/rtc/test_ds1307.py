# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

import sys
import time
import unittest

import test.conditions
from src.drivers.rtc.ds1307 import DS1307, DS1307_ADDRESS


def ds1307Present():
    if sys.implementation.name == "micropython" and "Pi Pico W" in sys.implementation._machine:
        import machine
        devices = machine.SoftI2C(machine.Pin(21),
                                  machine.Pin(20),
                                  freq=400_000
                                  ).scan()
        return DS1307_ADDRESS in devices
    return False


UNIX_TIMESTAMP = 1694982561
DATE = (2023, 9, 17, 20, 29, 21, 6)


@unittest.skipUnless(ds1307Present(), "No DS1307 present on standard I2C bus")
@test.conditions.external_devices_included()
class Ds1307DriverTest(unittest.TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        rtc = DS1307()
        rtc.disableIrqOnDevice()

    def test_device_reads_time(self):
        rtc = DS1307()
        (year, month, day, hour, minute, second, *_) = rtc.getTime()
        self.assertGreaterEqual(year, 2000)
        self.assertGreaterEqual(month, 1)
        self.assertGreaterEqual(day, 1)
        self.assertGreaterEqual(hour, 0)
        self.assertGreaterEqual(minute, 0)
        self.assertGreaterEqual(second, 0)

    def test_deviceUpdateUnixTimeAndGetUnixTime(self):
        rtc = DS1307()
        rtc.setUnixTime(UNIX_TIMESTAMP)
        time = rtc.getUnixTime()
        self.assertGreaterEqual(time, UNIX_TIMESTAMP)

    def test_deviceUpdateUnixTimeAndGetTime(self):
        rtc = DS1307()
        rtc.setUnixTime(UNIX_TIMESTAMP)
        result = rtc.getTime()
        self._assertGetTimeResult(result)

    def _assertGetTimeResult(self, result):
        (year, month, day, hour, minute, second, *_) = result
        (expected_year, expected_month, expected_day, expected_hour, expected_minute, expected_second, *_) = DATE
        self.assertEqual(year, expected_year)
        self.assertEqual(month, expected_month)
        self.assertEqual(day, expected_day)
        self.assertEqual(hour, expected_hour)
        self.assertEqual(minute, expected_minute)
        self.assertGreaterEqual(second, expected_second)

    def test_deviceUpdateTimeAndGetUnixTime(self):
        rtc = DS1307()
        rtc.setTime(DATE)
        time = rtc.getUnixTime()
        self.assertGreaterEqual(time, UNIX_TIMESTAMP)

    def test_deviceUpdateTimeAndGetTime(self):
        rtc = DS1307()
        rtc.setTime(DATE)
        result = rtc.getTime()
        self._assertGetTimeResult(result)

    @test.conditions.slow()
    def test_irqWorksWith1Hz(self):
        rtc = DS1307()

        self._count = 0

        def countIrq(pin):
            self._count = self._count + 1

        rtc.irq(countIrq)
        rtc.setIrqFrequency(1)
        rtc.enableIrq()

        time.sleep(4)
        rtc.disableIrq()

        self.assertGreaterEqual(self._count, 3)
        self.assertLessEqual(self._count, 5)

    def test_irqWorksWith4GHz(self):
        rtc = DS1307()

        self._count = 0

        def countIrq(pin):
            self._count = self._count + 1

        rtc.irq(countIrq)
        rtc.setIrqFrequency(4_096)
        rtc.enableIrq()

        time.sleep(1)
        rtc.disableIrq()

        # dealing with python and high frequencies...
        self.assertGreaterEqual(self._count, 4_040)
        self.assertLessEqual(self._count, 4_150)

    def test_irqWorksNotInvokedWhenDisabled(self):
        rtc = DS1307()

        self._count = 0

        def countIrq(pin):
            self._count = self._count + 1

        rtc.irq(countIrq)
        rtc.setIrqFrequency(4_096)
        rtc.disableIrq()

        time.sleep(1)

        # dealing with python and high frequencies...
        self.assertEqual(self._count, 0)

    def test_noIrqPinDefined(self):
        rtc = DS1307(irq_pin=None)

        def countIrq():
            pass

        with self.assertRaises(ValueError):
            rtc.irq(countIrq)

        with self.assertRaises(ValueError):
            rtc.enableIrq()

        with self.assertRaises(ValueError):
            rtc.disableIrq()


if __name__ == '__main__':
    unittest.main()

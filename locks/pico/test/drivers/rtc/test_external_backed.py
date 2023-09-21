# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

import unittest

import test.conditions
from src.drivers.rtc.external_backed import ExternalBackedRtc
from test.mock import Mock, Matchers

MOCKED_DATE = (2030, 3, 13, 15, 52, 31, 2)
UNIX_TIME = 1899647551
SET_DATE = (2030, 3, 12, 5, 41, 1, 0)
SET_UNIX_TIME = 1899524461


@test.conditions.micropython_only()
class TestExternalBackedRtc(unittest.TestCase):
    def setUp(self) -> None:
        self._mock = Mock(name="MockedRTC")

    def test_backedRtcReadFromDelegateOnInitOnly(self):
        self._mock.getTime.when().thenReturn(MOCKED_DATE)

        rtc = ExternalBackedRtc(self._mock)
        (year, month, day, hour, minute, second, weekday, *_) = rtc.getTime()

        (eyear, emonth, eday, ehour, eminute, esecond, eweekday) = MOCKED_DATE
        self.assertEqual((year, month, day, hour, minute, weekday), (eyear, emonth, eday, ehour, eminute, eweekday))
        self.assertGreaterEqual(second, esecond)
        self._mock.verify().getTime(Matchers.any()).called().notAtAll()
        self._mock.verify().getTime().called().once()
        self._mock.verify().getUnixTime().called().notAtAll()
        self._mock.verify().getUnixTime(Matchers.any()).called().notAtAll()

    def test_getUnixTimeDoNotCallDelegate(self):
        self._mock.getTime.when().thenReturn(MOCKED_DATE)

        rtc = ExternalBackedRtc(self._mock)
        result = rtc.getUnixTime()

        self.assertGreaterEqual(result, UNIX_TIME)
        self.assertLessEqual(result, UNIX_TIME + 1)
        self._mock.verify().getTime(Matchers.any()).called().notAtAll()
        self._mock.verify().getTime().called().once()
        self._mock.verify().getUnixTime().called().notAtAll()
        self._mock.verify().getUnixTime(Matchers.any()).called().notAtAll()

    def test_setTimeCallDelegateAndSetsTime(self):
        self._mock.getTime.when().thenReturn(MOCKED_DATE)
        self._mock.setTime.when(Matchers.any()).thenDoNothing()

        rtc = ExternalBackedRtc(self._mock)
        rtc.setTime(SET_DATE)
        result = rtc.getUnixTime()

        self.assertGreaterEqual(result, SET_UNIX_TIME)
        self.assertLessEqual(result, SET_UNIX_TIME + 1)
        self._mock.verify().setTime(SET_DATE).called().once()

    def test_setUnixTimeCallDelegateAndSetsTime(self):
        self._mock.getTime.when().thenReturn(MOCKED_DATE)
        self._mock.setTime.when(Matchers.any()).thenDoNothing()

        rtc = ExternalBackedRtc(self._mock)
        rtc.setUnixTime(SET_UNIX_TIME)
        result = rtc.getUnixTime()

        self.assertGreaterEqual(result, SET_UNIX_TIME)
        self.assertLessEqual(result, SET_UNIX_TIME + 1)
        self._mock.verify().setTime(Matchers.any()).called().once()

    def test_calledDelegateOnOtherMethods(self):
        self._mock = Mock(name="MockedRTC", deepMock=True)
        self._mock.getTime.when().thenReturn(MOCKED_DATE)
        self._mock.getAvailableIrqFrequencies.when().thenReturn(10)

        rtc = ExternalBackedRtc(self._mock)

        rtc.irq(1, arg=2)
        rtc.disableIrq()
        rtc.enableIrq()
        rtc.setIrqFrequency(5)
        result = rtc.getAvailableIrqFrequencies()

        self.assertEqual(result, 10)
        self._mock.verify().irq(1, arg=2).called().once()
        self._mock.verify().disableIrq().called().once()
        self._mock.verify().enableIrq().called().once()
        self._mock.verify().setIrqFrequency(5).called().once()
        self._mock.verify().getAvailableIrqFrequencies().called().once()


if __name__ == '__main__':
    unittest.main()

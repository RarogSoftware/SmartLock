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
from test.mock import Mock, Matchers


class TestMockThatWorkWithMicropython(unittest.TestCase):
    def test_mockingReturnValue(self):
        returnValue = 8
        mock = Mock(name="TestMock")
        mock.method.when().thenReturn(returnValue)
        self.assertEqual(mock.method(), returnValue)

    def test_mockingAttribute(self):
        value = 8
        mock = Mock(name="TestMock")
        mock.attribute = value
        self.assertEqual(mock.attribute, value)
        mock.attribute = None
        mock.verify().attribute.retrieved()
        mock.verify().attribute.set().exactly(times=2)
        mock.verify().attribute.removed().notAtAll()
        with self.assertRaises(AssertionError):
            mock.verify().attribute.retrieved().notAtAll()
        with self.assertRaises(AssertionError):
            mock.verify().attribute.set().once()
        with self.assertRaises(AssertionError):
            mock.verify().attribute.removed().once()

    def test_mockingAttributeAdvanced(self):
        value = 8
        mock = Mock(name="TestMock")
        mock.attribute = value
        del mock.attribute
        with self.assertRaises(AttributeError):
            mock.attribute
        mock.attribute = None

        mock.verify().attribute.retrieved().notAtAll()
        mock.verify().attribute.set().exactly(times=2)
        mock.verify().attribute.removed().once()
        with self.assertRaises(AssertionError):
            mock.verify().attribute.retrieved().once()
        with self.assertRaises(AssertionError):
            mock.verify().attribute.set().once()
        with self.assertRaises(AssertionError):
            mock.verify().attribute.removed().notAtAll()

    def test_nonDeepMockThrowsException(self):
        mock = Mock(name="TestMock")
        with self.assertRaises(AssertionError):
            mock.method()

    def test_deepMockAutoMocks(self):
        mock = Mock(name="TestMock", deepMock=True)

        singleMock = mock.method()
        parameterMock = mock.subobject.method()
        methodDoubleMock = mock.method().otherMethod()

        self.assertEqual(singleMock._mock_.mockName, "TestMock.method.()")
        self.assertEqual(parameterMock._mock_.mockName, "TestMock.subobject.method.()")
        self.assertEqual(methodDoubleMock._mock_.mockName, "TestMock.method.().otherMethod.()")

    def test_autoMocksSaveCalls(self):
        mock = Mock(name="TestMock", deepMock=True)

        mock.method()
        mock.subobject.method()
        mock.method().otherMethod()

        mock.verify().method().called().exactly(times=2)
        mock.subobject.verify().method().called().once()
        mock.method().verify().otherMethod().called().once()

    def test_mockWithArgumentsRememberArguments(self):
        mock = Mock(name="TestMock")

        returnValue1 = 8
        returnValue2 = "Val"

        mock.method.when(2, 3, "Test", name="Value").thenReturn(returnValue1)
        result1 = mock.method(2, 3, "Test", name="Value")

        mock.method.when(name="Value").thenReturn(returnValue2)
        result2 = mock.method(name="Value")

        with self.assertRaises(AssertionError):
            mock.method()

        self.assertEqual(result1, returnValue1)
        self.assertEqual(result2, returnValue2)

    def test_mockThrowException(self):
        mock = Mock("TestValue")

        mock.method.when().thenThrow(RuntimeError)

        with self.assertRaises(RuntimeError):
            mock.method()

    def test_mockInvocationFunction(self):
        mock = Mock("TestValue")

        mock.method.when(Matchers.any()).thenInvoke(lambda value: value)

        result = mock.method(23)

        self.assertEqual(result, 23)

    def test_assertNoInteractionsOnItself(self):
        mock = Mock(name="Test mock", deepMock=True)

        mock.verify().noInteractions()

        mock()

        with self.assertRaises(AssertionError):
            mock.verify().noInteractions()

    def test_assertNoInteractionsWithAttributes(self):
        mock = Mock(name="Test mock")

        mock.verify().noInteractions()

        mock.attr = 1

        with self.assertRaises(AssertionError):
            mock.verify().noInteractions()

    def test_assertNoInteractionsOnChildren(self):
        mock = Mock(name="Test mock", deepMock=True)
        mock.method.when().thenReturn(1)
        mock.object.method.when().thenReturn(2)

        mock.verify().noInteractions()

        mock.method()
        mock.object.method(1)

        with self.assertRaises(AssertionError):
            mock.verify().noInteractions()

    def test_assertCalledWithArguments(self):
        mock = Mock(name="Test mock")
        value = "Test"
        mock.method.when(Matchers.eq("arg"), kwarg=Matchers.gt(2)).thenReturn(value)

        returnValue = mock.method("arg", kwarg=4)

        self.assertEqual(returnValue, value)

        with self.assertRaises(AssertionError):
            mock.verify().method().called().notAtAll()
        mock.verify().method().called().once()
        mock.verify().method(1, "arg", kwarg=4).called().once()

    def test_dirContainsMockedMethods(self):
        mock = Mock()

        mock.method.when().thenReturn(1)
        mock.method2.when().thenReturn(2)

        self.assertTrue("method" in dir(mock))
        self.assertTrue("method2" in dir(mock))

    @test.conditions.pc_only()
    def test_appearAsType(self):
        mock = Mock(mockClass=unittest.TestCase)

        print(type(mock))
        print(issubclass(type(mock), unittest.TestCase))
        self.assertTrue(issubclass(type(mock), unittest.TestCase))

    def test_assertsForNonExistingValues(self):
        mock = Mock()

        mock.verify().attribute.noInteractions()
        mock.verify().method().noInteractions()

        mock.verify().attribute.accessed().notAtAll()
        mock.verify().method().called().notAtAll()

    def test_thatMocksAreLightEnoughToWorkOnDevice(self):
        mocks = []

        for i in range(0, 30):
            mock = Mock()

            mock.method1.when(1, 2, 3, 4, 5).thenReturn(2)
            mock.method2.when(1, 2, 3, 4, 5).thenReturn(2)
            mock.method3.when(1, 2, 3, 4, 5).thenReturn(2)

            for j in range(1, 20):
                mock.method1(1, 2, 3, 4, 5)

            mocks.append(mock)

        self.assertTrue(len(mocks), 30)


if __name__ == '__main__':
    unittest.main()

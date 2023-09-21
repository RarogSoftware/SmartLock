# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

from .mock_helpers import MockHelpers


class NumberAsserts:
    def __init__(self, message, number, parent):
        self._message = message
        self._number = number
        self._parent = parent

    def andVerify(self):
        return self._parent

    def times(self):
        return self.andVerify()

    def atLeast(self, times):
        if self._number >= times:
            raise AssertionError(f'{self._message} at least {times} times, but was {self._number} times')
        return self

    def atMost(self, times):
        if self._number <= times:
            raise AssertionError(f'{self._message} at most {times} times, but was {self._number} times')
        return self

    def exactly(self, times):
        if self._number != times:
            raise AssertionError(f'{self._message} exactly {times} times, but was {self._number} times')
        return self._parent

    def once(self):
        if self._number != 1:
            raise AssertionError(f'{self._message} once, but was {self._number} times')
        return self._parent

    def notAtAll(self):
        if self._number != 0:
            raise AssertionError(f'{self._message} not at all, but was {self._number} times')
        return self._parent


class MockMethodAsserts:
    def __init__(self, name, matches):
        self._name = name
        self._matches = matches

    def called(self):
        times = len(self._matches) if self._matches is not None else 0
        return NumberAsserts(f"Expected method {self._name} to be called", times, self)

    def noInteractions(self):
        self.called().notAtAll()


class MockAttributeAsserts:
    def __init__(self, name, attribute):
        self._attributeName = name
        self._attribute = attribute

    def __call__(self, *args, **kwargs):
        return MockMethodAsserts(self._attributeName, None)

    def noInteractions(self):
        self.accessed().notAtAll()

    def accessed(self):
        return NumberAsserts(f'Expected attribute {self._attributeName} to be accessed',
                             self._doIfAttributeExists(
                                 lambda: self._attribute["retrieved"] + self._attributeName + self._attribute[
                                     "removed"]),
                             self)

    def _doIfAttributeExists(self, function):
        if self._attribute is not None:
            return function()
        return 0

    def retrieved(self):
        return NumberAsserts(f'Expected attribute {self._attributeName} to be retrieved',
                             self._doIfAttributeExists(lambda: self._attribute["retrieved"]),
                             self)

    def set(self):
        return NumberAsserts(f'Expected attribute {self._attributeName} to be retrieved',
                             self._doIfAttributeExists(lambda: self._attribute["set"]), self)

    def removed(self):
        return NumberAsserts(f'Expected attribute {self._attributeName} to be retrieved',
                             self._doIfAttributeExists(lambda: self._attribute["removed"]), self)


class MockAsserts:
    def __init__(self, name, mockData, hasAttributes=True):
        self._mockName = name
        self._mockData = mockData
        self._hasAttributes = hasAttributes

    def __getattr__(self, item):
        if not self._hasAttributes:
            return super().__getattribute__(item)
        if item in self._mockData.attributes.keys():
            return MockAttributeAsserts(item, self._mockData.attributes[item])
        elif item in self._mockData.methods.keys():
            return MockAsserts(item, self._mockData.methods[item]._mock_, False)
        else:
            return MockAttributeAsserts(item, None)

    def __call__(self, *args, **kwargs):
        argsMatchers, kwargsMatchers = MockHelpers.convertArgumentsIntoMatchers(args, kwargs)
        matches = []

        for (args, kwargs) in self._mockData.calls:
            if len(args) == len(argsMatchers) and len(kwargsMatchers) == len(kwargsMatchers):
                matched = True
                for i in range(0, len(args)):
                    if not argsMatchers[i].match(args[i]):
                        matched = False
                        break
                if not matched:
                    continue

                for key in kwargsMatchers:
                    if key not in kwargs.keys() or not kwargsMatchers[key].match(kwargs[key]):
                        matched = False
                        break
                if not matched:
                    continue
                matches.append((args, kwargs))

        return MockMethodAsserts(self._mockName, matches)

    def noInteractions(self):
        if self._mockData is None:
            return
        for mock in self._mockData.methods.values():
            mock.verify().noInteractions()
        if len(self._mockData.attributes) != 0 or len(self._mockData.calls) != 0:
            raise AssertionError(f'\"{self._mockName}\" had interactions.\n' +
                                 f"Attributes interactions: {self._mockData.attributes}\n" +
                                 f"Methods interactions: {self._mockData.calls}")

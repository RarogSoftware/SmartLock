# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

from .mock_asserts import *
from .mock_helpers import *


class MockData:
    def __init__(self):
        self.deepMock = False
        self.mockName = ""
        self.mockedClass = None
        self.deepMockReturnedMock = None
        self.defaultReturnFunction = None
        self.argumentMatchedReturnFunctions = []
        self.calls = []
        self.methods = {}
        self.attributes = {}

    def deepMockReturnFunction(self, *args, **kwargs):
        if self.deepMockReturnedMock is None:
            self.deepMockReturnedMock = Mock(
                name=self.generateItemName(kwargs["_mock_calledMockName"], "()"), deepMock=True)
        return self.deepMockReturnedMock

    @staticmethod
    def generateItemName(mockName, item):
        if mockName is None:
            return item
        else:
            return f"{mockName}.{item}"

    def getMock(self, item):
        try:
            return self.methods[item]
        except KeyError:
            newMock = Mock(self.generateItemName(self.mockName, item), self.deepMock)
            self.methods[item] = newMock
            return newMock


class Mock:
    def __init__(self, name=None, deepMock=False, mockClass=None):
        self._mock_ = MockData()
        self._mock_.deepMock = deepMock
        self._mock_.mockName = name
        if deepMock:
            self._mock_.defaultReturnFunction = self._mock_.deepMockReturnFunction
        if mockClass is not None:
            currentDir = dir(type(self))
            for method in dir(mockClass):
                if method not in currentDir:
                    self.__getattr__(method)

    def __getattr__(self, item):
        if (item != "_mock_" and item != "when" and item != "assert" and not str(item).startswith("__")):
            if item in self._mock_.attributes.keys():
                if self._mock_.attributes[item]["removed"] < self._mock_.attributes[item]["set"]:
                    attr = self._mock_.attributes[item]
                    attr["retrieved"] = attr["retrieved"] + 1
                    return attr["value"]
                return getattr(super(), item)
            return self._mock_.getMock(item)
        raise AttributeError(f"Mock '{self._mock_.mockName}' has no attribute '{item}'")

    def __setattr__(self, key, value):
        if key == "when" or key == "verify" or key == "__setattr__":
            raise RuntimeError("Cannot override mock base methods")
        if not key.startswith("_mock_") and not key.startswith("__"):
            if key in self._mock_.methods.keys():
                raise ValueError(
                    f"Key {key} already defined as method. Mock do not allow overrides of this type as it usually indicates error. If you want to do this remove mocked method with del")
            if key in self._mock_.attributes.keys():
                self._mock_.attributes[key]["set"] = self._mock_.attributes[key]["set"] + 1
            else:
                self._mock_.attributes[key] = {
                    "value": value,
                    "retrieved": 0,
                    "set": 1,
                    "removed": 0
                }
            return value
        return super().__setattr__(key, value)

    def __delattr__(self, item):
        if item == "when" or item == "verify" or item == "__setattr__":
            raise RuntimeError("Cannot remove mock base methods")
        if not item.startswith("_mock_") and not item.startswith("__"):
            if item in self._mock_.attributes.keys():
                self._mock_.attributes[item]["removed"] = self._mock_.attributes[item]["removed"] + 1
                return
            if item in self._mock_.methods.keys():
                del self._mock_.methods[item]
                return
        return super().__delattr__(item)

    def __dir__(self):
        originalList = dir(super())
        for mock in self._mock_.methods.keys():
            originalList.append(mock)
        return originalList

    def __call__(self, *args, **kwargs):
        self._mock_.calls.append((args, kwargs))
        for (argsMatchers, kwargsMatchers, returnValue) in self._mock_.argumentMatchedReturnFunctions:
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

                return returnValue(*args, **kwargs)

        if self._mock_.defaultReturnFunction is None:
            raise AssertionError(f'Called unmocked method "{self._mock_.mockName}(args:{args}, kwargs:{kwargs})"')
        kwargs["_mock_calledMockName"] = self._mock_.mockName
        return self._mock_.defaultReturnFunction(*args, **kwargs)

    def __str__(self):
        return f"{self._mock_.mockName}(): {self._mock_.methods}"

    def when(self, *args, **kwargs):
        argMatchers, kwargsMatchers = MockHelpers.convertArgumentsIntoMatchers(args, kwargs)

        def appendFunction(invocationFunction):
            self._mock_.argumentMatchedReturnFunctions.append((argMatchers, kwargsMatchers, invocationFunction))

        return MockMethodConfig(appendFunction)

    def verify(self):
        return MockAsserts(self._mock_.mockName, self._mock_)

# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
from .argument_matchers import *


class MockMethodConfig:
    def __init__(self, appendFunction):
        self._function = appendFunction

    def thenReturn(self, value):
        self._function(lambda *args, **kwargs: value)

    def thenThrow(self, exception):
        def raiseException(*args, **kwargs):
            if type(exception) is type:
                raise exception()
            elif callable(exception):
                raise exception
            else:
                raise exception(*args, **kwargs)

        self._function(raiseException)

    def thenInvoke(self, invocation):
        self._function(invocation)


class MockHelpers:
    @staticmethod
    def convertArgumentsIntoMatchers(args, kwargs):
        argMatchers = []
        kwargsMatchers = {}
        for arg in args:
            argMatchers.append(MockHelpers.getArgumentMatcher(arg))
        for key in kwargs:
            kwargsMatchers[key] = MockHelpers.getArgumentMatcher(kwargs[key])
        return argMatchers, kwargsMatchers

    @staticmethod
    def getArgumentMatcher(arg):
        if issubclass(type(arg), ArgumentMatcher):
            argMatcher = arg
        else:
            argMatcher = EqMatcher(arg)
        return argMatcher

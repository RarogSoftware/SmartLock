# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------


class Matchers:
    """Helper for easy access of all predefined matchers"""

    @staticmethod
    def eq(value):
        return EqMatcher(value)

    @staticmethod
    def gt(value):
        return GreaterThanMatcher(value)

    @staticmethod
    def any():
        return AnyMatcher()


class ArgumentMatcher:
    """Used for expressing dynamic arguments when defining method signature in Mock.when() or Mock.assert()"""

    def match(self, value) -> bool: ...


class EqMatcher(ArgumentMatcher):
    def __init__(self, value):
        self._value = value

    def match(self, value):
        return self._value == value

    def __str__(self):
        return f"eq({self._value})"


class GreaterThanMatcher(ArgumentMatcher):
    def __init__(self, value):
        self._value = value

    def match(self, value):
        return self._value <= value

    def __str__(self):
        return f"gt({self._value})"


class AnyMatcher(ArgumentMatcher):
    def match(self, value) -> bool:
        return True

    def __str__(self):
        return "any()"

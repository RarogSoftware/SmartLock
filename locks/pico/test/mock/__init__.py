# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
#
# Simple implementation of mocking library that works well enough with micropython
# and can be used on low memory devices like RPI Pico, Arduino, ESP32, etc.
# This library allows to mock methods and attributes of mocked class and later
# assert if mocks were invoked with expected parameter, amount of times, etc.
#
# API is loosely inspired Mockito library for Java
#
# Note that full mocks are naturally extremely heavy as they store data of
# each invocation, as well as as use complicated internal structures to
# allow for dynamic behaviour control. If you need a lot of mocks,
# it is recommended to use stub objects instead.
#

from .argument_matchers import Matchers
from .mock import Mock

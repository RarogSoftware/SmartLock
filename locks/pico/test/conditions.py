# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

import sys
import unittest

from .test_runner import config


def pc_only():
    return unittest.skipUnless(sys.implementation.name == "cpython",
                               "This test works only on cPython aka PC version of python")


def micropython_only():
    return unittest.skipUnless(sys.implementation.name == "micropython", "This test works only on micropython")


def device_only():
    return unittest.skipUnless(sys.implementation.name == "micropython" and "Pi Pico W" in sys.implementation._machine,
                               "This test works only on Pico W")


def external_devices_included():
    try:
        condition = config['DEVICES_TESTS']
    except KeyError:
        condition = False
    return unittest.skipUnless(condition, "No external devices tests were ran")


def slow():
    try:
        condition = config['SLOWS_TESTS']
    except KeyError:
        condition = False
    return unittest.skipUnless(condition, "No slow tests were ran")

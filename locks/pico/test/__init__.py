# ------------------------------------------------------------------------------
#  Copyright (c) 2023 onwards, Pawel Przytarski                                -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

import sys

from .test_runner import config

if sys.implementation.name == 'micropython':
    from .test_runner import run_tests
elif sys.implementation.name == "cpython":
    import test.micropython_mocks

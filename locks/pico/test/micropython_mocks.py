# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------
import sys

def get_micropython_mocks():
    from unittest.mock import MagicMock
    import test.mock.micropython.micropython as micropython
    import test.mock.micropython.machine as machine
    import test.mock.micropython.aioble as aioble

    return dict({
        "micropython": micropython,
        "collections": {
            "abc": MagicMock()
        },
        "aioble": aioble,
        "bluetooth": MagicMock(),
        "machine": machine
    })


if "micropython" != sys.implementation.name:
    print("Mocking micropython libraries")
    mocks = get_micropython_mocks()
    for key in mocks:
        sys.modules[key] = mocks[key]

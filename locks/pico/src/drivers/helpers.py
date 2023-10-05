# ------------------------------------------------------------------------------
#  Copyright (c) 2023, Pawel Przytarski                                        -
#                                                                              -
#   Licensed under the Apache License, Version 2.0 (the "License");            -
#   you may not use this file except in compliance with the License.           -
#   You may obtain a copy of the License at                                    -
#   http://www.apache.org/licenses/LICENSE-2.0                                 -
# ------------------------------------------------------------------------------

from machine import Pin

PinLike = Pin


class PinHelpers:
    @staticmethod
    def pinLikeToOutPin(pinLike: PinLike, name: str):
        PinHelpers.checkIsPinLike(name, pinLike)

        if isinstance(pinLike, int):
            return Pin(pinLike, Pin.OUT)

        pinLike.init(Pin.OUT)
        return pinLike

    @staticmethod
    def pinLikeToInPin(pinLike: PinLike, name: str, pull: int = -1):
        PinHelpers.checkIsPinLike(name, pinLike)

        if isinstance(pinLike, int):
            return Pin(pinLike, Pin.IN, pull)

        pinLike.init(Pin.IN, pull)
        return pinLike

    @staticmethod
    def checkIsPinLike(name, pinLike):
        if not isinstance(pinLike, Pin) and not isinstance(pinLike, int):
            raise ValueError(f"{name} must be valid machine.Pin or number of pin")

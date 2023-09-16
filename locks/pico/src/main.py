import asyncio

import aioble
import bluetooth
from micropython import const

_CURRENT_API = const("0.0")
# lock service/namespace
_LOCK_SERVICE_UUID = bluetooth.UUID("c5114819-7312-44df-a60e-0e004d52cdf2")
# lockState
_LOCK_STATE_UUID = bluetooth.UUID("53ffd6da-faea-5711-861b-2c823b4d37f3")
# apiVersion
_LOCK_API_VERSION_UUID = bluetooth.UUID("26084787-dd2e-573c-9909-50fa997d8d70")
# commandRx
_LOCK_COMMAND_UUID = bluetooth.UUID("1007179b-8749-5c02-ae48-7fdc43307ef8")
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE = const(576)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 550_000

# Register GATT server.
lock_service = aioble.Service(_LOCK_SERVICE_UUID)
lock_state = aioble.Characteristic(lock_service, _LOCK_STATE_UUID, read=True, notify=True, initial="UNKNOWN")
lock_api = aioble.Characteristic(lock_service, _LOCK_STATE_UUID, read=True, initial=_CURRENT_API)
lock_command = aioble.Characteristic(lock_service, _LOCK_COMMAND_UUID, write=True, capture=True)
aioble.register_services(lock_service)


# struct.pack("<h", int(`value`))


lock_command.read()


async def run_ble_service():
    while True:
        try:
            async with await aioble.advertise(
                    _ADV_INTERVAL_MS,
                    name="MyLockService",
                    services=[_LOCK_SERVICE_UUID],
                    appearance=_ADV_APPEARANCE,
            ) as connection:
                try:
                    while connection.is_connected():
                        (device, data) = await lock_command.written(timeout_ms=60000)
                        print(data)
                except TimeoutError:
                    await connection.disconnected(timeout_ms=10000)
        except KeyboardInterrupt:
            break
        except Exception as error:
            print("Error in BLE connection handling: " + error)


async def main():
    ble_service = asyncio.create_task(run_ble_service())
    await asyncio.gather(ble_service)

def start():
    asyncio.run(main())

if __name__ == "__main__":
    start()

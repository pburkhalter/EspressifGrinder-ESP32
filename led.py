import uasyncio
from config import pinLED


async def blink_led(interval):
    while True:
        pinLED.on()
        await uasyncio.sleep(interval / 1000)
        pinLED.off()
        await uasyncio.sleep(interval / 1000)


class LEDController:
    def __init__(self, pin=pinLED):
        self.pin = pin
        self.__task = None

    async def _blink(self, interval, duration):
        try:
            uasyncio.wait_for(blink_led(interval), duration)
        finally:
            self.pin.off()

    def blink(self, interval=500, duration=0):
        self.cancel()  # Cancel any ongoing blinking before starting a new one
        self.__task = uasyncio.create_task(self._blink(interval, duration))

    def cancel(self):
        if self.__task:
            self.__task.cancel()
            self.__task = None

    def on(self):
        self.cancel()
        self.pin.on()

    def off(self):
        self.cancel()
        self.pin.off()

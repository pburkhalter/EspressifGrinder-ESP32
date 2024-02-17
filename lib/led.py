import asyncio


async def blink_led(pin, interval):
    try:
        while True:
            pin.on()
            await asyncio.sleep(interval / 1000)
            pin.off()
            await asyncio.sleep(interval / 1000)
    except asyncio.CancelledError:
        pin.off()


class LED:
    def __init__(self, pin):
        self.pin = pin
        self.__task = None

    async def _blink(self, interval, duration):
        if duration:
            await asyncio.wait_for(blink_led(self.pin, interval), duration)
        else:
            await blink_led(self.pin, interval)

    def blink(self, interval, duration=None):
        self.cancel()  # Cancel any ongoing blinking before starting a new one
        self.__task = asyncio.create_task(self._blink(interval, duration))

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

import math
import uasyncio
from config import pinLED


async def blink_led(interval, duration):
    blinks = math.floor(duration / (interval * 2))
    try:
        for i in range(blinks):
            pinLED.on()
            await uasyncio.sleep_ms(interval)
            pinLED.off()
            await uasyncio.sleep_ms(interval)
    except uasyncio.CancelledError:
        pinLED.off()


class LEDController:

    def __init__(self):
        self.interval = 500

        self.__task = None

    def blink(self, interval, duration=0):
        if interval:
            self.interval = interval

        self.__task = uasyncio.create_task(blink_led(self.interval, duration))

    def cancel(self):
        try:
            self.__task.cancel()
        except uasyncio.CancelledError:
            pass

    def on(self):
        self.cancel()
        pinLED.on()

    def off(self):
        self.cancel()
        pinLED.off()


statusLED = LEDController()
import asyncio
from config import conf, pinGRN, pinSMO, pinLED
from lib.led import LED


async def grind(duration):
    led = LED(pinLED)
    try:
        print("Grinding started...")
        pinGRN.on()
        led.on()
        await asyncio.sleep(duration / 1000)
    except asyncio.CancelledError:
        print("Grinding cancelled...")
        led.blink(250, conf.data['grinder']['memorize_timeout'])
    finally:
        pinGRN.off()
        led.off()
        print("Grinding completed or stopped.")


class GrinderController:
    def __init__(self):
        self.__mode = None
        self.__duration = 0
        self.__task = None
        self.set_mode("single" if pinSMO.value() == 0 else "double")

    def set_mode(self, mode):
        self.__mode = mode
        print(f"Switching to {mode} mode...")
        self.__duration = conf.data['grinder'][mode]
        self.stop_grinding()

    def start_grinding(self):
        self.cancel_grinding_task()
        self.__task = asyncio.create_task(grind(self.__duration))

    def stop_grinding(self):
        self.cancel_grinding_task()
        self.update_stats()

    def cancel_grinding_task(self):
        if self.__task:
            self.__task.cancel()
            self.__task = None

    def update_stats(self):
        # Update stats only if the mode is already set
        if self.__mode:
            conf.data['stats'][self.__mode] += 1
            # Reset duration to original based on the mode after grinding stops
            self.__duration = conf.data['grinder'][self.__mode]


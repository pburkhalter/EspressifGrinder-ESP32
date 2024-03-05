import asyncio
import time

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
        led.blink(250, conf.data['grinder']['duration']['memorize'])
    finally:
        pinGRN.off()
        led.off()
        print("Grinding completed or stopped.")


def start_count():
    return time.ticks_ms()


def elapsed_time_since(start_ticks):
    current_ticks = time.ticks_ms()
    elapsed_time = time.ticks_diff(current_ticks, start_ticks)
    return elapsed_time


class GrinderController:
    def __init__(self):
        self.__task = None
        self.__modeset = None
        self.__mode = None
        self.__duration = 0
        self.__ticks_current = 0
        self.__ticks_total = 0

        self.set_mode("single" if pinSMO.value() == 0 else "double")

    def set_mode(self, mode):
        self.__mode = mode
        self.__duration = conf.data['grinder']['duration'][mode]
        self.stop_grinding()

    def start_grinding(self):
        self.check_mode()
        self.cancel_grinding_task()

        self.__ticks_current = start_count()
        self.__task = asyncio.create_task(grind(self.__duration))

    def stop_grinding(self):
        self.__ticks_total = self.__ticks_total + elapsed_time_since(self.__ticks_current)
        self.cancel_grinding_task()
        # self.update_stats()

    def cancel_grinding_task(self):
        if self.__task:
            self.__task.cancel()
            self.__task = None

    def update_stats(self):
        # Update stats only if the mode is already set
        if self.__mode:
            conf.data['stats'][self.__mode] += 1
            # Reset duration to original based on the mode after grinding stops
            self.__duration = conf.data['grinder']['duration'][self.__mode]

    def check_mode(self):
        self.__modeset = conf.grinder['modeset']
        if self.__modeset == 'learn':
            # in learning mode, set duration to 60s
            self.__duration = 60000

        if conf.grinder['modeset'] != 'learn' and self.__modeset == 'learn':
            # not in learning mode anymore, save to config
            self.__modeset = conf.grinder['modeset']
            conf.data['grinder']['duration'][self.__mode] = self.__ticks_total
            conf.save()

import uasyncio
from config import conf, pinGRN, pinSMO
from led import LEDController


async def grind(duration):
    led_controller = LEDController()
    try:
        print("Grinding started...")
        pinGRN.on()
        led_controller.on()
        await uasyncio.sleep_ms(duration)
    except uasyncio.CancelledError:
        print("Grinding cancelled...")
        led_controller.blink(250, conf.data['grinder']['memorize_timeout'])
    finally:
        pinGRN.off()
        led_controller.off()
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
        self.__task = uasyncio.create_task(grind(self.__duration))

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


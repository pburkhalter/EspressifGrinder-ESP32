import time
import uasyncio
from config import conf, pinD1, pinD5


async def grind(duration):
    try:
        print("Grinding started...")
        pinD1.on()
        await uasyncio.sleep_ms(duration)
        pinD1.off()
        print("Grinding completed...")
    except uasyncio.CancelledError:
        pinD1.off()
        print("Grinding cancelled...")


class GrinderController(object):

    def __init__(self):
        self.__mode = None        # Grinder-mode
        self.__duration = 0       # Set the current grinder time based on mode
        self.__started = None     # Time Grind started (ticks)
        self.__stopped = None     # Time Grind stopped (ticks)
        self.__task = None        # Async grinding task

        if pinD5.value() == 0:
            self.set_mode("single")
        else:
            self.set_mode("double")

    def get_mode(self):
        return self.__mode

    def set_mode(self, mode):
        if mode == "single":
            print("Switching to single mode...")
            self.__mode = "single"
            self.__duration = conf.data['grinder']['single']
        if mode == "double":
            print("Switching to double mode...")
            self.__mode = "double"
            self.__duration = conf.data['grinder']['double']
        
        self.stop()
        self.__started = None
        self.__stopped = None

    def reset(self):
        if self.__mode == "single":
            conf.data['stats']['single'] += 1
            self.__duration = int(conf.data['grinder']['single'])
        else:
            conf.data['stats']['double'] += 1
            self.__duration = int(conf.data['grinder']['double'])

        self.__started = None
        self.__stopped = None   

    def start(self):            
        if self.__stopped:
            diff_elapsed_stop = time.ticks_diff(time.ticks_ms(), self.__stopped)
            
            if diff_elapsed_stop >= int(conf.data['grinder']['memorize_timeout']):
                self.reset()
                print("Last grind was %s ms ago, limit is %s ms, starting over (%s ms left)..." % (diff_elapsed_stop, conf.data['grinder']['memorize_timeout'], self.__duration))
            else:
                diff_elapsed_grind = time.ticks_diff(self.__stopped, self.__started)

                self.__duration -= diff_elapsed_grind 
                if self.__duration > 0:
                    print("Resuming grinding (%s ms left)..." % (self.__duration, ))
                else:
                    self.reset()

        self.__started = time.ticks_ms()
        self.__task = uasyncio.create_task(grind(self.__duration))

    def stop(self):
        self.__stopped = time.ticks_ms()
        diff_elapsed_grind = time.ticks_diff(self.__started, self.__stopped)
            
        if diff_elapsed_grind >= self.__duration:
            self.reset()
        
        try:     
            self.__task.cancel()
        except AttributeError:
            pass

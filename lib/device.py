import gc
import os
import machine


class DeviceInfo:

    @property
    def mem_total(self):
        return self.mem_free + self.mem_used

    @property
    def mem_free(self):
        gc.collect()
        return gc.mem_free()

    @property
    def mem_used(self):
        return gc.mem_alloc()

    @property
    def disk_total(self):
        # Total size in bytes = Block size * Number of blocks
        stat = os.statvfs("/")
        size = stat[1] * stat[2]
        return size // 1024  # Convert to KB

    @property
    def disk_free(self):
        # Free space in bytes = Block size * Number of free blocks
        stat = os.statvfs("/")
        free = stat[0] * stat[3]
        return free // 1024  # Convert to KB

    @property
    def disk_used(self):
        # Used space in bytes = Total size - Free space
        used = self.disk_total * 1024 - self.disk_free * 1024
        return used // 1024  # Convert back to KB

    @property
    def cpu_freq(self):
        return machine.freq()

    @property
    def model(self):
        return os.uname().sysname

    @property
    def node(self):
        return os.uname().nodename

    @property
    def version(self):
        return os.uname().version

    @property
    def machine(self):
        return os.uname().machine


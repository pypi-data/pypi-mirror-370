from psutil._common import shwtemp, snetio


class UsageMock:
    ru_utime = 1
    ru_stime = 1


class CpuFreqMock:
    current = 1234


class SwapMemoryMock:
    percent = 123


class PsutilMock:

    def boot_time(self):
        return 1234567890

    def getloadavg(self):
        return (1, 2, 3)

    def cpu_freq(self):
        return CpuFreqMock

    def cpu_percent(self, interval=None):
        return 12

    def swap_memory(self):
        return SwapMemoryMock

    def sensors_temperatures(self):
        return {
            'coretemp': [
                shwtemp(label='Package id 0', current=53.0, high=100.0, critical=100.0),
                shwtemp(label='Core 0', current=50.0, high=100.0, critical=100.0),
                shwtemp(label='Core 4', current=51.0, high=100.0, critical=100.0),
            ],
            'nvme': [
                shwtemp(label='Composite', current=32.85, high=81.85, critical=84.85),
            ],
        }

    def net_io_counters(self, pernic):
        return {
            'eth0': snetio(
                bytes_sent=123,
                bytes_recv=456,
                packets_sent=0,
                packets_recv=0,
                errin=0,
                errout=0,
                dropin=0,
                dropout=0,
            ),
        }

    def Process(self, pid):
        class ProcessMock:
            def create_time(self):
                return 1234567890

            def cpu_percent(self, interval=None):
                return 12

        return ProcessMock()

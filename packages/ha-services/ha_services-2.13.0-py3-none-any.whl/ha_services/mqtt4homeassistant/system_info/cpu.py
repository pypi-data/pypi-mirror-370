import os

import psutil

from ha_services.mqtt4homeassistant.components.sensor import Sensor


class CpuFreqSensor(Sensor):

    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'CPU frequency')
        kwargs.setdefault('uid', 'cpu_freq')
        kwargs.setdefault('device_class', 'frequency')
        kwargs.setdefault('state_class', 'measurement')
        kwargs.setdefault('unit_of_measurement', 'MHz')
        kwargs.setdefault('suggested_display_precision', 0)
        kwargs.setdefault('min_value', 1)  # Less than 1MHz ?
        kwargs.setdefault('max_value', 20_000)  # More than 20.000MHz ?
        super().__init__(**kwargs)

    def publish_state(self, *args, **kwargs):
        # Update the state, before publishing:
        info = psutil.cpu_freq()
        self.set_state(int(info.current))
        return super().publish_state(*args, **kwargs)


class SystemLoad1MinSensor(Sensor):

    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'System load 1min.')
        kwargs.setdefault('uid', 'system_load_1min')
        kwargs.setdefault('state_class', 'measurement')
        kwargs.setdefault('suggested_display_precision', 2)
        kwargs.setdefault('min_value', 0)
        super().__init__(**kwargs)

    def publish_state(self, *args, **kwargs):
        # Update the state, before publishing:
        self.set_state(psutil.getloadavg()[0])
        return super().publish_state(*args, **kwargs)


class TotalCpuUsageSensor(Sensor):

    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'Total CPU usage')
        kwargs.setdefault('uid', 'total_cpu_usage')
        kwargs.setdefault('unit_of_measurement', '%')
        kwargs.setdefault('suggested_display_precision', 1)
        kwargs.setdefault('min_value', 0)
        kwargs.setdefault('max_value', 100)
        super().__init__(**kwargs)

    def publish_state(self, *args, **kwargs):
        # Update the state, before publishing:
        self.set_state(psutil.cpu_percent(interval=None))
        return super().publish_state(*args, **kwargs)


class ProcessCpuUsageSensor(Sensor):

    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'Process CPU usage')
        kwargs.setdefault('uid', 'process_cpu_usage')
        kwargs.setdefault('unit_of_measurement', '%')
        kwargs.setdefault('suggested_display_precision', 1)
        kwargs.setdefault('min_value', 0)
        kwargs.setdefault('max_value', 100)
        super().__init__(**kwargs)

        self.process = psutil.Process(os.getpid())

    def publish_state(self, *args, **kwargs):
        # Update the state, before publishing:
        self.set_state(self.process.cpu_percent(interval=None))
        return super().publish_state(*args, **kwargs)

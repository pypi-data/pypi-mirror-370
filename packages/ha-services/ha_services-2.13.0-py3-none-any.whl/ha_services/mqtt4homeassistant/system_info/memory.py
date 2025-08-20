import psutil

from ha_services.mqtt4homeassistant.components.sensor import Sensor


class SwapUsageSensor(Sensor):
    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'Swap usage')
        kwargs.setdefault('uid', 'swap_usage')
        kwargs.setdefault('unit_of_measurement', '%')
        kwargs.setdefault('suggested_display_precision', 1)
        super().__init__(**kwargs)

    def publish_state(self, *args, **kwargs):
        # Update the state, before publishing:
        swap = psutil.swap_memory()
        self.set_state(swap.percent)
        return super().publish_state(*args, **kwargs)

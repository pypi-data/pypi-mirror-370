import datetime

from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.utilities.system_utils import get_system_start_datetime, process_start_datetime


class UpTimeSensor(Sensor):
    """
    Sensor for the system up time.
    Adds the datetime when the system was started to Home Assistant.
    """

    def __init__(self, **kwargs):
        # https://www.home-assistant.io/integrations/sensor/#device-class
        kwargs.setdefault('device_class', 'timestamp')
        kwargs.setdefault('name', 'System Up Time')
        kwargs.setdefault('uid', 'up_time')
        super().__init__(**kwargs)

        # Set only one time. No need to update.
        system_start: datetime.datetime = get_system_start_datetime()
        self.set_state(system_start.isoformat())


class StartTimeSensor(Sensor):
    """
    Sensor for project start time.
    """

    def __init__(self, **kwargs):
        # https://www.home-assistant.io/integrations/sensor/#device-class
        kwargs.setdefault('device_class', 'timestamp')
        kwargs.setdefault('name', 'Process Start')
        kwargs.setdefault('uid', 'process_start')
        super().__init__(**kwargs)

        # Set only one time. No need to update.
        process_start: datetime.datetime = process_start_datetime()
        self.set_state(process_start.isoformat())

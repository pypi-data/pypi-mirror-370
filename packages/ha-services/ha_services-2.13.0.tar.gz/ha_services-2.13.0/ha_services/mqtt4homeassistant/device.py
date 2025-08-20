import logging
import socket

from frozendict import frozendict
from paho.mqtt.client import Client

from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.system_info.cpu import (
    CpuFreqSensor,
    ProcessCpuUsageSensor,
    SystemLoad1MinSensor,
    TotalCpuUsageSensor,
)
from ha_services.mqtt4homeassistant.system_info.memory import SwapUsageSensor
from ha_services.mqtt4homeassistant.system_info.netstat import NetStatSensors
from ha_services.mqtt4homeassistant.system_info.temperatures import TemperaturesSensors
from ha_services.mqtt4homeassistant.system_info.up_time import StartTimeSensor, UpTimeSensor
from ha_services.mqtt4homeassistant.system_info.wifi_info import WifiInfo2Mqtt
from ha_services.mqtt4homeassistant.utilities.assertments import assert_uid


logger = logging.getLogger(__name__)


class BaseMqttDevice:
    device_uids = set()
    components = {}  # Global registry of all components

    def __init__(
        self,
        *,
        name: str,
        uid: str,
        topic_prefix: str = 'homeassistant',
        manufacturer: str | None = None,
        model: str | None = None,
        sw_version: str | None = None,
        throttle_sec: int = 1,  # min. time between state publishing
        config_throttle_sec: int = 20,  # Min. time between config publishing
    ):
        self.name = name

        assert_uid(uid)
        assert uid not in MqttDevice.device_uids, f'Duplicate uid: {uid}'
        self.uid = uid
        self.topic_prefix = topic_prefix

        self.manufacturer = manufacturer
        self.model = model
        self.sw_version = sw_version

        self.throttle_sec = throttle_sec
        self.config_throttle_sec = config_throttle_sec

        self._mqtt_payload_cache = None

    def register_component(self, *, component):
        logger.debug(f'Registering component: {component}')

        from ha_services.mqtt4homeassistant.components import BaseComponent

        assert isinstance(component, BaseComponent)
        uid = component.uid
        assert uid not in self.components, f'Duplicate component: {uid}'
        self.components[uid] = component


class MqttDevice(BaseMqttDevice):
    def __init__(self, *, main_device: BaseMqttDevice | None = None, **kwargs):
        super().__init__(**kwargs)

        if main_device:
            self.via_device = main_device.uid
            self.uid = f'{main_device.uid}-{self.uid}'

    def get_mqtt_payload(self) -> dict:
        if self._mqtt_payload_cache is None:
            mqtt_payload = {
                'name': self.name,
                'identifiers': self.uid,
            }
            for key in ('via_device', 'manufacturer', 'model', 'sw_version'):
                if value := getattr(self, key, None):
                    mqtt_payload[key] = value
            self._mqtt_payload_cache = frozendict(mqtt_payload)

        return self._mqtt_payload_cache


class MainMqttDevice(MqttDevice):
    def __init__(self, **kwargs):
        assert 'main_device' not in kwargs, 'main_device is not allowed for MainMqttDevice'
        super().__init__(**kwargs)

        self.hostname = Sensor(
            device=self,
            name='Hostname',
            uid='hostname',
        )

        self.up_time_sensor = UpTimeSensor(device=self)
        self.process_start_sensor = StartTimeSensor(device=self)
        self.cpu_freq_sensor = CpuFreqSensor(device=self)
        self.swap_usage = SwapUsageSensor(device=self)

        self.system_load_1min = SystemLoad1MinSensor(device=self)
        self.total_cpu_usage = TotalCpuUsageSensor(device=self)
        self.process_cpu_usage = ProcessCpuUsageSensor(device=self)

        self.temperatures_sensors = TemperaturesSensors(device=self)
        self.netstat_sensors = NetStatSensors(device=self)

        self.wifi_info_sensors = WifiInfo2Mqtt(device=self)

    def poll_and_publish(self, client: Client) -> None:
        logger.debug(f'Polling {self.name} ({self.uid})')

        self.hostname.set_state(socket.gethostname())
        self.hostname.publish(client)

        self.up_time_sensor.publish(client)
        self.process_start_sensor.publish(client)
        self.cpu_freq_sensor.publish(client)
        self.swap_usage.publish(client)

        self.system_load_1min.publish(client)
        self.total_cpu_usage.publish(client)
        self.process_cpu_usage.publish(client)

        self.temperatures_sensors.publish(client)
        self.netstat_sensors.publish(client)

        self.wifi_info_sensors.poll_and_publish(client)

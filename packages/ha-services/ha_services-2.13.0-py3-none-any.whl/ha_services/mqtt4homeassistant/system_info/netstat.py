import logging
import time
import typing

from paho.mqtt.client import Client
from psutil._common import snetio

from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.utilities.string_utils import slugify
from ha_services.mqtt4homeassistant.utilities.system_utils import netstat


if typing.TYPE_CHECKING:
    from ha_services.mqtt4homeassistant.device import MqttDevice


logger = logging.getLogger(__name__)


class NetStatSensor:
    def __init__(self, *, device: 'MqttDevice', interface_name: str):
        logger.info('Creating net stat sensor for: %r', interface_name)

        self.device = device
        self.interface_name = interface_name

        self.bytes_sent_old = 0
        self.bytes_sent_sensor = Sensor(
            device=self.device,
            name=f'{interface_name} sent',
            uid=slugify(f'{interface_name}_sent'),
            device_class='data_size',
            state_class='measurement',
            unit_of_measurement='KiB',
            suggested_display_precision=1,
        )
        self.bytes_sent_rate_sensor = Sensor(
            device=self.device,
            name=f'{interface_name} sent rate',
            uid=slugify(f'{interface_name}_sent_rate'),
            device_class='data_rate',
            state_class='measurement',
            unit_of_measurement='KiB/s',
            suggested_display_precision=1,
        )

        self.bytes_received_old = 0
        self.bytes_received_sensor = Sensor(
            device=self.device,
            name=f'{interface_name} received',
            uid=slugify(f'{interface_name}_received'),
            device_class='data_size',
            state_class='measurement',
            unit_of_measurement='KiB',
            suggested_display_precision=1,
        )
        self.bytes_received_rate_sensor = Sensor(
            device=self.device,
            name=f'{interface_name} received rate',
            uid=slugify(f'{interface_name}_received_rate'),
            device_class='data_rate',
            state_class='measurement',
            unit_of_measurement='KiB/s',
            suggested_display_precision=1,
        )
        self.last_update = time.monotonic()

    def set_state(self, data: snetio) -> None:
        update_duration = time.monotonic() - self.last_update
        self.last_update = time.monotonic()

        bytes_sent = data.bytes_sent / 1024
        self.bytes_sent_sensor.set_state(bytes_sent)
        bytes_sent_rate = (bytes_sent - self.bytes_sent_old) / update_duration
        self.bytes_sent_rate_sensor.set_state(bytes_sent_rate)
        self.bytes_sent_old = bytes_sent

        bytes_received = data.bytes_recv / 1024
        self.bytes_received_sensor.set_state(bytes_received)
        bytes_received_rate = (bytes_received - self.bytes_received_old) / update_duration
        self.bytes_received_rate_sensor.set_state(bytes_received_rate)
        self.bytes_received_old = bytes_received

    def publish(self, client):
        self.bytes_sent_sensor.publish(client)
        self.bytes_sent_rate_sensor.publish(client)
        self.bytes_received_sensor.publish(client)
        self.bytes_received_rate_sensor.publish(client)


class NetStatSensors:
    """
    Expose sent/received value from all interesting network interfaces as MQTT sensors.
    """

    def __init__(self, device: 'MqttDevice'):
        self.device = device
        self.sensors = {}
        self.set_state()  # Add sensors

    def set_state(self):
        data = netstat()
        for interface_name, interface_data in data.items():
            try:
                sensor = self.sensors[interface_name]
            except KeyError:
                sensor = NetStatSensor(
                    device=self.device,
                    interface_name=interface_name,
                )
                self.sensors[interface_name] = sensor
            sensor.set_state(interface_data)

    def publish(self, client: Client) -> None:
        self.set_state()
        for sensors in self.sensors.values():
            sensors.publish(client)

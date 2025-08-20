import logging
from unittest import TestCase

from ha_services.exceptions import InvalidStateValue
from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.data_classes import NO_STATE, ComponentConfig, ComponentState
from ha_services.mqtt4homeassistant.device import MqttDevice
from ha_services.tests.base import ComponentTestMixin


class SensorTestCase(ComponentTestMixin, TestCase):
    def test_mimimal_sensor(self):
        with self.assertNoLogs(level=logging.WARNING):
            sensor = Sensor(
                device=MqttDevice(name='My device', uid='device_id'),
                name='My component',
                uid='component_id',
            )
            self.assertEqual(
                sensor.get_config(),
                ComponentConfig(
                    topic='homeassistant/sensor/device_id/device_id-component_id/config',
                    payload={
                        'component': 'sensor',
                        'device': {'identifiers': 'device_id', 'name': 'My device'},
                        'device_class': None,
                        'json_attributes_topic': 'homeassistant/sensor/device_id/device_id-component_id/attributes',
                        'name': 'My component',
                        'state_class': None,
                        'state_topic': 'homeassistant/sensor/device_id/device_id-component_id/state',
                        'unique_id': 'device_id-component_id',
                        'unit_of_measurement': None,
                    },
                ),
            )
            self.assertEqual(
                sensor.get_state(),
                ComponentState(
                    topic='homeassistant/sensor/device_id/device_id-component_id/state',
                    payload=NO_STATE,  # no initial state -> NO_STATE
                ),
            )
            sensor.set_state(123)
            self.assertEqual(
                sensor.get_state(),
                ComponentState(
                    topic='homeassistant/sensor/device_id/device_id-component_id/state',
                    payload=123,  # now we have a state
                ),
            )

    def test_min_max_validation(self):
        with self.assertNoLogs(level=logging.WARNING):
            sensor = Sensor(
                device=MqttDevice(name='My device', uid='device_id'),
                name='My component',
                uid='component_id',
                min_value=-10,
                max_value=10,
            )
            self.assertEqual(
                sensor.get_config(),
                ComponentConfig(
                    topic='homeassistant/sensor/device_id/device_id-component_id/config',
                    payload={
                        'component': 'sensor',
                        'device': {'identifiers': 'device_id', 'name': 'My device'},
                        'device_class': None,
                        'json_attributes_topic': 'homeassistant/sensor/device_id/device_id-component_id/attributes',
                        'name': 'My component',
                        'state_class': None,
                        'state_topic': 'homeassistant/sensor/device_id/device_id-component_id/state',
                        'unique_id': 'device_id-component_id',
                        'unit_of_measurement': None,
                    },
                ),
            )
            self.assertEqual(
                sensor.get_state(),
                ComponentState(
                    topic='homeassistant/sensor/device_id/device_id-component_id/state',
                    payload=NO_STATE,  # no initial state -> NO_STATE
                ),
            )

            with self.assertRaises(InvalidStateValue) as cm:
                sensor.set_state(-123.456)
            self.assertEqual(
                str(cm.exception),
                "Sensor(self.uid='device_id-component_id'): state=-123.456 is smaller than self.min_value=-10",
            )

            with self.assertRaises(InvalidStateValue) as cm:
                sensor.set_state('Bam!')
            self.assertEqual(
                str(cm.exception), "Sensor(self.uid='device_id-component_id'): state='Bam!' is not a number"
            )

            with self.assertRaises(InvalidStateValue) as cm:
                sensor.set_state(123)
            self.assertEqual(
                str(cm.exception),
                "Sensor(self.uid='device_id-component_id'): state=123 is bigger than self.max_value=10",
            )

            sensor.set_state(5)
            self.assertEqual(
                sensor.get_state(),
                ComponentState(
                    topic='homeassistant/sensor/device_id/device_id-component_id/state',
                    payload=5,  # now we have a state
                ),
            )

    def test_full_sensor(self):
        with self.assertNoLogs(level=logging.WARNING):
            sensor = Sensor(
                device=MqttDevice(name='My device', uid='device_id'),
                name='My component',
                uid='component_id',
                component='sensor',
                device_class='temperature',
                state_class='measurement',
                unit_of_measurement='°C',
                suggested_display_precision=2,
            )
            self.assertEqual(
                sensor.get_config(),
                ComponentConfig(
                    topic='homeassistant/sensor/device_id/device_id-component_id/config',
                    payload={
                        'component': 'sensor',
                        'device': {'identifiers': 'device_id', 'name': 'My device'},
                        'device_class': 'temperature',
                        'json_attributes_topic': 'homeassistant/sensor/device_id/device_id-component_id/attributes',
                        'name': 'My component',
                        'state_class': 'measurement',
                        'state_topic': 'homeassistant/sensor/device_id/device_id-component_id/state',
                        'suggested_display_precision': 2,
                        'unique_id': 'device_id-component_id',
                        'unit_of_measurement': '°C',
                    },
                ),
            )
            self.assertEqual(
                sensor.get_state(),
                ComponentState(
                    topic='homeassistant/sensor/device_id/device_id-component_id/state',
                    payload=NO_STATE,  # no initial state -> NO_STATE
                ),
            )
            sensor.set_state(456)
            self.assertEqual(
                sensor.get_state(),
                ComponentState(
                    topic='homeassistant/sensor/device_id/device_id-component_id/state',
                    payload=456,  # now we have a state
                ),
            )

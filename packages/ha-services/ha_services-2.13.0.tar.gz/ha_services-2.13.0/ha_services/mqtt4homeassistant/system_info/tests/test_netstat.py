import logging
from unittest import TestCase

from bx_py_utils.test_utils.snapshot import assert_snapshot

from ha_services.mqtt4homeassistant.data_classes import ComponentState
from ha_services.mqtt4homeassistant.device import MqttDevice
from ha_services.mqtt4homeassistant.mocks import HostSystemMock
from ha_services.mqtt4homeassistant.mocks.mqtt_client_mock import MqttClientMock
from ha_services.mqtt4homeassistant.system_info.netstat import NetStatSensor, NetStatSensors


class NetStatSensorsTestCase(TestCase):
    maxDiff = None

    def test_happy_path(self):
        def get_sensors_data(netstat_sensors):
            data = {}
            for interface_name, sensor in netstat_sensors.sensors.items():
                state = sensor.bytes_sent_sensor.get_state()
                self.assertIsInstance(state, ComponentState)
                data[interface_name] = state
            return data

        with HostSystemMock(), self.assertNoLogs(level=logging.WARNING):
            netstat_sensors = NetStatSensors(
                device=MqttDevice(name='foo', uid='bar'),
            )
            self.assertEqual(
                get_sensors_data(netstat_sensors),
                {
                    'eth0': ComponentState(
                        topic='homeassistant/sensor/bar/bar-eth0sent/state',
                        payload=0.1201171875,  # Mocked value
                    )
                },
            )

            sensor = netstat_sensors.sensors['eth0']
            self.assertIsInstance(sensor, NetStatSensor)
            self.assertEqual(
                sensor.bytes_sent_sensor.get_state().topic,
                'homeassistant/sensor/bar/bar-eth0sent/state',
            )

            mqtt_client_mock = MqttClientMock()
            netstat_sensors.publish(mqtt_client_mock)

            self.assertEqual(
                mqtt_client_mock.get_state_messages(),
                [
                    {
                        'topic': 'homeassistant/sensor/bar/bar-eth0sent/state',
                        'payload': 0.1201171875,
                        'qos': 0,
                        'retain': False,
                    },
                    {
                        'topic': 'homeassistant/sensor/bar/bar-eth0sentrate/state',
                        'payload': 0.0,
                        'qos': 0,
                        'retain': False,
                    },
                    {
                        'topic': 'homeassistant/sensor/bar/bar-eth0received/state',
                        'payload': 0.4453125,
                        'qos': 0,
                        'retain': False,
                    },
                    {
                        'topic': 'homeassistant/sensor/bar/bar-eth0receivedrate/state',
                        'payload': 0.0,
                        'qos': 0,
                        'retain': False,
                    },
                ],
            )

            config_payload = mqtt_client_mock.get_config_payload()
            # Check sample:
            self.assertEqual(
                config_payload[0],
                {
                    'component': 'sensor',
                    'device': {'identifiers': 'bar', 'name': 'foo'},
                    'device_class': 'data_size',
                    'json_attributes_topic': 'homeassistant/sensor/bar/bar-eth0sent/attributes',
                    'name': 'eth0 sent',
                    'origin': {
                        'name': 'ha-services-tests',
                        'support_url': 'https://pypi.org/project/ha_services/',
                        'sw_version': '1.2.3',
                    },
                    'state_class': 'measurement',
                    'state_topic': 'homeassistant/sensor/bar/bar-eth0sent/state',
                    'suggested_display_precision': 1,
                    'unique_id': 'bar-eth0sent',
                    'unit_of_measurement': 'KiB',
                },
            )
            assert_snapshot(got=config_payload)

            state_messages = mqtt_client_mock.get_state_messages()
            # Check sample:
            self.assertEqual(
                state_messages[0],
                {
                    'topic': 'homeassistant/sensor/bar/bar-eth0sent/state',
                    'payload': 0.1201171875,
                    'qos': 0,
                    'retain': False,
                },
            )
            assert_snapshot(got=state_messages)

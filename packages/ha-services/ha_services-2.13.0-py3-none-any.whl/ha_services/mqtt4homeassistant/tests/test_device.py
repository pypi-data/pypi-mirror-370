import logging
from unittest import TestCase

from frozendict import frozendict

from ha_services.mqtt4homeassistant.components.switch import Switch
from ha_services.mqtt4homeassistant.device import MainMqttDevice, MqttDevice
from ha_services.tests.base import ComponentTestMixin


class DeviceTestCase(ComponentTestMixin, TestCase):
    def test_device(self):
        with self.assertNoLogs(level=logging.WARNING):
            device = MqttDevice(name='My Device', uid='device1')
            self.assertEqual(
                device.get_mqtt_payload(),
                {'name': 'My Device', 'identifiers': 'device1'},
            )
            self.assertEqual(device.topic_prefix, 'homeassistant')
            self.assertEqual(device.uid, 'device1')

            switch1 = Switch(device=device, name='My Switch 1', uid='switch1')
            switch2 = Switch(device=device, name='My Switch 2', uid='switch2')

            with self.assertRaises(AssertionError) as cm:
                Switch(device=device, name='My Switch 1', uid='switch1')
            self.assertEqual(str(cm.exception), 'Duplicate component: device1-switch1')

            self.assertEqual(
                device.components,
                {
                    'device1-switch1': switch1,
                    'device1-switch2': switch2,
                },
            )

    def test_device_with_main_device(self):
        with self.assertNoLogs(level=logging.WARNING):
            main_device = MainMqttDevice(name='Main Device', uid='main_device')
            device = MqttDevice(main_device=main_device, name='Sub Device', uid='sub_device')
            self.assertEqual(
                device.get_mqtt_payload(),
                {
                    'name': 'Sub Device',
                    'identifiers': 'main_device-sub_device',
                    'via_device': 'main_device',
                },
            )
            self.assertEqual(device.topic_prefix, 'homeassistant')
            self.assertEqual(device.uid, 'main_device-sub_device')

    def test_device_extras(self):
        with self.assertNoLogs(level=logging.WARNING):
            device = MqttDevice(
                name='My Device',
                uid='device1',
                manufacturer='Tinkerforge',
                model='HAT Zero Brick',
                sw_version='1.2.3',
            )
            mqtt_payload = device.get_mqtt_payload()
            self.assertEqual(
                mqtt_payload,
                {
                    'name': 'My Device',
                    'identifiers': 'device1',
                    'manufacturer': 'Tinkerforge',
                    'model': 'HAT Zero Brick',
                    'sw_version': '1.2.3',
                },
            )
            self.assertIsInstance(mqtt_payload, frozendict)

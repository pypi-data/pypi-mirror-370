import dataclasses
import logging
import socket
from unittest import TestCase

from ha_services.mqtt4homeassistant.data_classes import MqttSettings
from ha_services.mqtt4homeassistant.utilities.string_utils import slugify
from ha_services.tests.base import ComponentTestMixin


class DataClassesTestCase(ComponentTestMixin, TestCase):
    def test_mqtt_settings(self):
        with self.assertNoLogs(level=logging.ERROR):
            mqtt_settings = MqttSettings()
        self.assertEqual(
            dataclasses.asdict(mqtt_settings),
            {
                'host': 'mqtt.eclipseprojects.io',
                'port': 1883,
                'password': '',
                'user_name': '',
                'main_uid': slugify(socket.gethostname(), sep='_'),
                'publish_config_throttle_seconds': 20,
                'publish_throttle_seconds': 5,
            },
        )

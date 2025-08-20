import logging
from unittest import TestCase
from unittest.mock import patch

from bx_py_utils.test_utils.snapshot import assert_snapshot

from ha_services.mqtt4homeassistant.device import MqttDevice
from ha_services.mqtt4homeassistant.mocks import HostSystemMock
from ha_services.mqtt4homeassistant.mocks.mqtt_client_mock import MqttClientMock
from ha_services.mqtt4homeassistant.system_info import wifi_info
from ha_services.mqtt4homeassistant.system_info.wifi_info import (
    WifiInfo,
    WifiInfo2Mqtt,
    WifiInfoValue,
    _convert_iwconfig_values,
    _get_iwconfig_values,
    get_wifi_infos,
)


class WifiInfoTestCase(TestCase):
    def test_happy_path(self):
        with HostSystemMock(), self.assertNoLogs(level=logging.WARNING):
            iwconfig_values = _get_iwconfig_values()
        self.assertEqual(
            iwconfig_values,
            {
                'wlo1': {
                    'ESSID': 'foobar',
                    'bit_rate': '29.2',
                    'bit_rate_unit': 'Mb/s',
                    'frequency': '5.18',
                    'frequency_unit': 'GHz',
                    'link_quality': '45/70',
                    'signal_level': '-65',
                    'signal_level_unit': 'dBm',
                }
            },
        )

        ##########################################################################################

        WIFI_INFOS = [
            WifiInfo(
                device_name='wlo1',
                values=[
                    WifiInfoValue(slug='ESSID', name='Essid', value='foobar', unit=None),
                    WifiInfoValue(slug='bit_rate', name='Bit rate', value=29.2, unit='Mb/s'),
                    WifiInfoValue(slug='frequency', name='Frequency', value=5.18, unit='GHz'),
                    WifiInfoValue(slug='link_quality', name='Link quality', value='45/70', unit=None),
                    WifiInfoValue(slug='signal_level', name='Signal level', value=-65, unit='dBm'),
                ],
            )
        ]

        self.assertEqual(_convert_iwconfig_values(iwconfig_values), WIFI_INFOS)

        ##########################################################################################

        with HostSystemMock(), self.assertNoLogs(level=logging.WARNING):
            wifi_infos = get_wifi_infos()
        self.assertEqual(wifi_infos, WIFI_INFOS)

        ##########################################################################################

        with self.assertNoLogs(level=logging.WARNING):
            mqtt_client_mock = MqttClientMock()
            wifi_info2mqtt = WifiInfo2Mqtt(
                device=MqttDevice(name='Main Device', uid='main_uid'),
            )

            with patch.object(wifi_info, 'get_wifi_infos', return_value=WIFI_INFOS):
                wifi_info2mqtt.poll_and_publish(client=mqtt_client_mock)

        # Some pre-checks:
        topics = [msg['topic'] for msg in mqtt_client_mock.messages]
        self.assertEqual(
            topics,
            [
                'homeassistant/sensor/main_uid/main_uid-wifi_device_name/config',
                'homeassistant/sensor/main_uid/main_uid-wifi_device_name/state',
                'homeassistant/sensor/main_uid/main_uid-ESSID/config',
                'homeassistant/sensor/main_uid/main_uid-ESSID/state',
                'homeassistant/sensor/main_uid/main_uid-bit_rate/config',
                'homeassistant/sensor/main_uid/main_uid-bit_rate/state',
                'homeassistant/sensor/main_uid/main_uid-frequency/config',
                'homeassistant/sensor/main_uid/main_uid-frequency/state',
                'homeassistant/sensor/main_uid/main_uid-link_quality/config',
                'homeassistant/sensor/main_uid/main_uid-link_quality/state',
                'homeassistant/sensor/main_uid/main_uid-signal_level/config',
                'homeassistant/sensor/main_uid/main_uid-signal_level/state',
            ],
        )
        for message in mqtt_client_mock.messages:
            topic = message['topic']
            payload = message['payload']
            self.assertIsInstance(payload, (int, float, str), message)
            if topic.endswith('/state'):
                if 'bit_rate' in topic:
                    self.assertEqual(payload, 29.2)
                elif 'frequency' in topic:
                    self.assertEqual(payload, 5.18)

        assert_snapshot(got=mqtt_client_mock.messages)

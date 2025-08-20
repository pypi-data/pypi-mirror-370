import logging
from unittest import TestCase

from ha_services.exceptions import InvalidStateValue
from ha_services.mqtt4homeassistant.components.select import Select
from ha_services.mqtt4homeassistant.data_classes import ComponentConfig, ComponentState
from ha_services.mqtt4homeassistant.device import MqttDevice


class SelectTestCase(TestCase):
    def test_select(self):
        with self.assertNoLogs(level=logging.WARNING):
            select = Select(
                device=MqttDevice(name='My Device', uid='device1'),
                name='My Select',
                uid='select1',
                options=('Option 1', 'Option 2'),
                default_option='Option 1',
            )
            self.assertEqual(
                select.get_config(),
                ComponentConfig(
                    topic='homeassistant/select/device1/device1-select1/config',
                    payload={
                        'command_topic': 'homeassistant/select/device1/device1-select1/command',
                        'component': 'select',
                        'device': {'identifiers': 'device1', 'name': 'My Device'},
                        'json_attributes_topic': 'homeassistant/select/device1/device1-select1/attributes',
                        'name': 'My Select',
                        'options': ('Option 1', 'Option 2'),
                        'state_topic': 'homeassistant/select/device1/device1-select1/state',
                        'unique_id': 'device1-select1',
                    },
                ),
            )
            self.assertEqual(
                select.get_state(),
                ComponentState(topic='homeassistant/select/device1/device1-select1/state', payload='Option 1'),
            )
            with self.assertRaises(InvalidStateValue) as cm:
                select.set_state('invalid_state')
            self.assertEqual(
                str(cm.exception),
                (
                    "Select(self.uid='device1-select1'):"
                    " state='invalid_state' not in self.options=('Option 1', 'Option 2')"
                ),
            )

            select.set_state('Option 2')
            self.assertEqual(
                select.get_state(),
                ComponentState(topic='homeassistant/select/device1/device1-select1/state', payload='Option 2'),
            )

import logging
from collections.abc import Callable

from paho.mqtt.client import MQTT_ERR_SUCCESS, Client, MQTTMessageInfo

from ha_services.exceptions import InvalidStateValue
from ha_services.mqtt4homeassistant.components import BaseComponent
from ha_services.mqtt4homeassistant.data_classes import NO_STATE, ComponentConfig, ComponentState
from ha_services.mqtt4homeassistant.device import MqttDevice


logger = logging.getLogger(__name__)


def default_select_callback(*, client: Client, component: BaseComponent, old_state: str, new_state: str):
    logger.info(f'{component.name} state changed: {old_state!r} -> {new_state!r}')
    component.set_state(new_state)
    component.publish_state(client)


class Select(BaseComponent):
    """
    MQTT Select component for Home Assistant.
    https://www.home-assistant.io/integrations/select.mqtt/
    """

    def __init__(
        self,
        *,
        device: MqttDevice,
        name: str,
        uid: str,
        callback: Callable = default_select_callback,
        component: str = 'select',
        initial_state=NO_STATE,  # set_state() must be called to set the value
        options: tuple[str, ...],
        default_option: str,
    ):
        super().__init__(
            device=device,
            name=name,
            uid=uid,
            component=component,
            initial_state=initial_state,
        )

        self.callback = callback

        self.options = options
        self.set_state(default_option)

        self.command_topic = f'{self.topic_prefix}/command'

    def _command_callback(self, client: Client, userdata, message: MQTTMessageInfo):
        new_state = message.payload.decode()
        assert new_state in self.options, f'Receive invalid state: {new_state!r}'

        self.callback(client=client, component=self, old_state=self.state, new_state=new_state)

    def publish_config(self, client: Client) -> MQTTMessageInfo:
        info = super().publish_config(client)

        client.message_callback_add(self.command_topic, self._command_callback)
        result, _ = client.subscribe(self.command_topic)
        if result is not MQTT_ERR_SUCCESS:
            logger.error(f'Error subscribing {self.command_topic=}: {result=}')

        return info

    def validate_state(self, state: str):
        super().validate_state(state)
        if state not in self.options:
            raise InvalidStateValue(component=self, error_msg=f'{state=} not in {self.options=}')

    def get_state(self) -> ComponentState:
        # e.g.: {'topic': 'homeassistant/select/My-device/My-Relay/state', 'payload': 'ON'}
        return ComponentState(
            topic=f'{self.topic_prefix}/state',
            payload=self.state,
        )

    def get_config(self) -> ComponentConfig:
        return ComponentConfig(
            topic=f'{self.topic_prefix}/config',
            payload={
                'component': self.component,
                'device': self.device.get_mqtt_payload(),
                'name': self.name,
                'unique_id': self.uid,
                'state_topic': f'{self.topic_prefix}/state',
                'json_attributes_topic': f'{self.topic_prefix}/attributes',
                'command_topic': self.command_topic,
                'options': self.options,
            },
        )

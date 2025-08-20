import json

from paho.mqtt.client import Client


class MqttClientMock(Client):
    def __init__(self):
        self.messages = []

    def publish(self, **kwargs) -> None:
        self.messages.append(kwargs)

    def _reset_sockets(self):
        pass

    def get_config_payload(self):
        config_payload = [
            json.loads(message['payload']) for message in self.messages if message['topic'].endswith('/config')
        ]
        return config_payload

    def get_state_messages(self):
        state_messages = [message for message in self.messages if message['topic'].endswith('/state')]
        return state_messages

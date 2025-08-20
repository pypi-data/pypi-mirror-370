import dataclasses
import logging
import os
import random
import resource
import time

from cli_base.systemd.data_classes import BaseSystemdServiceInfo, BaseSystemdServiceTemplateContext
from paho.mqtt.client import Client
from rich import print  # noqa

import ha_services
from ha_services.exceptions import InvalidStateValue
from ha_services.mqtt4homeassistant.components.binary_sensor import BinarySensor
from ha_services.mqtt4homeassistant.components.select import Select
from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.components.switch import Switch
from ha_services.mqtt4homeassistant.data_classes import MqttSettings
from ha_services.mqtt4homeassistant.device import MainMqttDevice, MqttDevice
from ha_services.mqtt4homeassistant.mqtt import get_connected_client


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SystemdServiceTemplateContext(BaseSystemdServiceTemplateContext):
    """
    HaServices Demo - Context values for the systemd service file content.
    """

    verbose_service_name: str = 'HaServices Demo'


@dataclasses.dataclass
class SystemdServiceInfo(BaseSystemdServiceInfo):
    """
    HaServices Demo - Information for systemd helper functions.
    """

    template_context: SystemdServiceTemplateContext = dataclasses.field(default_factory=SystemdServiceTemplateContext)


@dataclasses.dataclass
class MqttExampleValues:
    """
    Some values used to create DEMO MQTT messages.
    """

    mqtt_payload_prefix: str = 'example'
    device_name: str = 'ha-services-demo'

    publish_config_throttle_seconds: int = 10  # Min. time between config publishing
    publish_throttle_seconds: int = 1  # Min. time between state publishing


@dataclasses.dataclass
class DemoSettings:
    """
    This are just settings for the "ha-services" DEMO.
    Will be used in ha_services example commands.
    See "./cli.py --help" for more information.
    """

    # Information how to setup the systemd services:
    systemd: dataclasses = dataclasses.field(default_factory=SystemdServiceInfo)

    # Information about the MQTT server:
    mqtt: dataclasses = dataclasses.field(default_factory=MqttSettings)

    # Example "app" data:
    app: dataclasses = dataclasses.field(default_factory=MqttExampleValues)


def publishing(*, user_settings: DemoSettings, verbosity: int, endless_loop: bool = True):
    """
    Publish "something" to MQTT server. It's just a DEMO ;)
    """

    main_device = MainMqttDevice(
        name='ha-services Main Device Example',
        uid=user_settings.mqtt.main_uid,
        manufacturer='ha_services',
        model='Just the example.py ;)',
        sw_version=ha_services.__version__,
        throttle_sec=user_settings.mqtt.publish_throttle_seconds,
        config_throttle_sec=user_settings.mqtt.publish_config_throttle_seconds,
    )

    device = MqttDevice(
        main_device=main_device,
        name='ha-services Sub Device Example',
        uid='ha_services_sub',
        manufacturer='ha_services',
        model='Just the example.py ;)',
        sw_version=ha_services.__version__,
        throttle_sec=user_settings.app.publish_throttle_seconds,
        config_throttle_sec=user_settings.app.publish_config_throttle_seconds,
    )

    activate_relay = BinarySensor(
        device=device,
        name='Activate Relay',
        uid='activate_relay',
        device_class=None,  # None == Generic ON/OFF or e.g.: 'door', 'motion', etc...
    )

    relay_delay = Sensor(
        device=device,
        name='Relay "delay"',
        uid='relay_delay',
        state_class='measurement',
        unit_of_measurement='sec',
    )

    select = Select(
        device=device,
        name='Select',
        uid='select',
        options=('Option 1', 'Option 2', 'Option 3'),
        default_option='Option 1',
    )

    def relay_callback(*, client: Client, component: Switch, old_state: str, new_state: str):
        logger.info(f'{component.name} state changed: {old_state!r} -> {new_state!r}')
        delay = random.randrange(5)
        logger.info(f'{delay=}')

        if not activate_relay.is_on:
            logger.info('Relay is not activated!')
            return

        relay_delay.set_state(delay)
        relay_delay.publish(mqttc)
        time.sleep(delay)

        component.set_state(new_state)
        component.publish_state(client)

    relay = Switch(
        device=device,
        name='Virtual Relay',
        uid='relay',
        callback=relay_callback,
    )
    system_load_sensor = Sensor(
        device=device,
        name='System load 1min.',
        uid='system_load',
        state_class='measurement',
        suggested_display_precision=2,
    )
    user_time_used_sensor = Sensor(
        device=device,
        name='Time in user mode (float seconds)',
        uid='user_time_used',
        state_class='measurement',
        unit_of_measurement='sec',
        suggested_display_precision=2,
    )
    system_time_used_sensor = Sensor(
        device=device,
        name='Time in system mode (float seconds)',
        uid='system_time_used',
        state_class='measurement',
        unit_of_measurement='sec',
        suggested_display_precision=2,
    )

    mqttc = get_connected_client(settings=user_settings.mqtt, verbosity=verbosity)
    mqttc.loop_start()

    relay.set_state(relay.OFF if random.randrange(2) else relay.ON)

    while True:
        try:
            main_device.poll_and_publish(mqttc)

            activate_relay.set_state(relay.OFF if random.randrange(2) else relay.ON)
            activate_relay.publish(mqttc)

            relay.publish(mqttc)
            select.publish(mqttc)

            system_load_sensor.set_state(os.getloadavg()[0])
            system_load_sensor.publish(mqttc)

            usage = resource.getrusage(resource.RUSAGE_SELF)
            user_time_used_sensor.set_state(usage.ru_utime)
            user_time_used_sensor.publish(mqttc)

            system_time_used_sensor.set_state(usage.ru_stime)
            system_time_used_sensor.publish(mqttc)
        except InvalidStateValue as err:
            logger.warning('Skip invalid state: %s', err)
        else:
            if not endless_loop:
                logger.info('Exiting...')
                break

        print('\n', flush=True)
        print('Wait', end='...')
        for i in range(10, 1, -1):
            time.sleep(0.5)
            print(i, end='...', flush=True)

    return main_device

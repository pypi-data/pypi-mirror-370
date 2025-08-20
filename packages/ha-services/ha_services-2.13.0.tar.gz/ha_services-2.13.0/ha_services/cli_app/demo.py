import logging

from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import print  # noqa

from ha_services.cli_app import app
from ha_services.cli_app.settings import get_user_settings
from ha_services.example import DemoSettings, publishing
from ha_services.mqtt4homeassistant.data_classes import MqttSettings
from ha_services.mqtt4homeassistant.mqtt import get_connected_client
from ha_services.mqtt4homeassistant.utilities.debug import print_components


logger = logging.getLogger(__name__)


@app.command
def test_mqtt_connection(verbosity: TyroVerbosityArgType):
    """
    Test connection to MQTT Server
    """
    setup_logging(verbosity=verbosity)
    user_settings: DemoSettings = get_user_settings(debug=True)

    settings: MqttSettings = user_settings.mqtt
    mqttc = get_connected_client(settings=settings, verbosity=verbosity)
    mqttc.loop_start()
    mqttc.loop_stop()
    mqttc.disconnect()
    print('\n[green]Test succeed[/green], bye ;)')


@app.command
def publish_loop(verbosity: TyroVerbosityArgType):
    """
    Publish data via MQTT for Home Assistant (endless loop)
    """
    setup_logging(verbosity=verbosity)
    user_settings: DemoSettings = get_user_settings(debug=True)

    try:
        publishing(user_settings=user_settings, verbosity=verbosity, endless_loop=True)
    except KeyboardInterrupt:
        print('Bye, bye')


@app.command
def info(verbosity: TyroVerbosityArgType):
    """
    Publish data once and display information about all registered components.
    """
    setup_logging(verbosity=verbosity)
    user_settings: DemoSettings = get_user_settings(debug=True)

    try:
        main_device = publishing(user_settings=user_settings, verbosity=verbosity, endless_loop=False)
    except KeyboardInterrupt:
        print('Bye, bye')
    else:
        print_components(main_device)

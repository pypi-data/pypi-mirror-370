import logging

from cli_base.cli_tools.verbosity import setup_logging
from cli_base.toml_settings.api import TomlSettings
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import print  # noqa

from ha_services.cli_app import app
from ha_services.example import DemoSettings


logger = logging.getLogger(__name__)


SETTINGS_DIR_NAME = 'ha-services'
SETTINGS_FILE_NAME = 'ha-services-demo'


def get_toml_settings() -> TomlSettings:
    return TomlSettings(
        dir_name=SETTINGS_DIR_NAME,
        file_name=SETTINGS_FILE_NAME,
        settings_dataclass=DemoSettings(),
    )


def get_user_settings(debug=True) -> DemoSettings:
    toml_settings: TomlSettings = get_toml_settings()
    user_settings: DemoSettings = toml_settings.get_user_settings(debug=True)
    return user_settings


@app.command
def edit_settings(verbosity: TyroVerbosityArgType):
    """
    Edit the settings file. On first call: Create the default one.
    """
    setup_logging(verbosity=verbosity)
    toml_settings: TomlSettings = get_toml_settings()
    toml_settings.open_in_editor()


@app.command
def print_settings(verbosity: TyroVerbosityArgType):
    """
    Display (anonymized) MQTT server username and password
    """
    setup_logging(verbosity=verbosity)
    toml_settings: TomlSettings = get_toml_settings()
    toml_settings.print_settings()

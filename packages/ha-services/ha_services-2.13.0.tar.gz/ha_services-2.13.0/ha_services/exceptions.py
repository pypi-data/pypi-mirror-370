import typing


if typing.TYPE_CHECKING:
    from ha_services.mqtt4homeassistant.components import BaseComponent


class HaServicesBaseException(Exception):
    """Base class for all exceptions raised by ha_services."""


class InvalidStateValue(HaServicesBaseException):
    def __init__(self, *, component: 'BaseComponent', error_msg: str):
        self.component = component
        self.error_msg = error_msg
        super().__init__(f'{component}: {error_msg}')

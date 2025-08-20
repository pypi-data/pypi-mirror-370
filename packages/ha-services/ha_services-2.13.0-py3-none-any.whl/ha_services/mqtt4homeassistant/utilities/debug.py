from rich import print  # noqa

from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.device import MainMqttDevice


def print_components(main_device: MainMqttDevice):
    print('\nList all registered components:')

    for index, component in enumerate(main_device.components.values(), start=1):
        print(f'\n{index}. {component.__class__.__name__}:')
        print(f'\tname: [green]{component.name}')
        if isinstance(component, Sensor):
            print(f'\tdevice_class: {component.device_class}')
            print(f'\tstate_class: {component.state_class}')
            state = component.get_state()
            print(f'\tstate: [blue]{state.payload}[/blue] [yellow]{component.unit_of_measurement}')
        print(f'\tthrottle: {component.throttle_sec} seconds')
        print(f'\tconfig throttle: {component.config_throttle_sec} seconds')

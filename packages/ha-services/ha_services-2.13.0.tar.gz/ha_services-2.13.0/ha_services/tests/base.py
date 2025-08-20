from ha_services.mqtt4homeassistant.device import BaseMqttDevice


class ComponentTestMixin:
    """
    Clear components to avoid side effects in other tests
    """

    def _clear_components(self):
        BaseMqttDevice.components.clear()

    def setUp(self):
        super().setUp()
        self._clear_components()

    def tearDown(self):
        super().tearDown()
        self._clear_components()

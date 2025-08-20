import datetime
from unittest.mock import patch

from bx_py_utils.test_utils.context_managers import MassContextManager

from ha_services.mqtt4homeassistant.components import get_origin_data
from ha_services.mqtt4homeassistant.mocks.psutil_mock import PsutilMock
from ha_services.mqtt4homeassistant.system_info import wifi_info


IWCONFIG_MOCK_OUTPUT = """
lo        no wireless extensions.

docker0   no wireless extensions.

wlo1      IEEE 802.11  ESSID:"foobar"
          Mode:Managed  Frequency:5.18 GHz  Access Point: 12:34:56:78:AB:CD
          Bit Rate=29.2 Mb/s   Tx-Power=22 dBm
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:on
          Link Quality=45/70  Signal level=-65 dBm
          Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
          Tx excessive retries:0  Invalid misc:511   Missed beacon:0
"""


class HostSystemMock(MassContextManager):
    def __init__(self):

        psutil_mock = PsutilMock()

        origin_data = get_origin_data()
        origin_data['name'] = 'ha-services-tests'
        origin_data['sw_version'] = '1.2.3'

        self.mocks = (
            patch('ha_services.mqtt4homeassistant.components.get_origin_data', return_value=origin_data),
            patch('ha_services.mqtt4homeassistant.device.socket.gethostname', return_value='TheHostName'),
            #
            patch('ha_services.mqtt4homeassistant.system_info.cpu.psutil', psutil_mock),
            patch('ha_services.mqtt4homeassistant.system_info.memory.psutil', psutil_mock),
            patch('ha_services.mqtt4homeassistant.system_info.temperatures.psutil', psutil_mock),
            patch('ha_services.mqtt4homeassistant.utilities.system_utils.psutil', psutil_mock),
            #
            patch.object(wifi_info, 'verbose_check_output', return_value=IWCONFIG_MOCK_OUTPUT),
            #
            # https://github.com/spulec/freezegun/issues/472
            patch("freezegun.api.tzlocal", lambda: datetime.UTC),
        )

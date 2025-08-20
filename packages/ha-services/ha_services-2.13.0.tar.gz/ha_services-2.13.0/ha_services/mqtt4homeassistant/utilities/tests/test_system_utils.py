import datetime
from unittest import TestCase

from freezegun import freeze_time

from ha_services.mqtt4homeassistant.mocks import HostSystemMock
from ha_services.mqtt4homeassistant.utilities.system_utils import get_system_start_datetime, process_start_datetime


class SystemUtilsTestCase(TestCase):

    def test_get_system_start_datetime(self):
        start_dt = get_system_start_datetime()
        self.assertIsInstance(start_dt, datetime.datetime)
        with (
            HostSystemMock(),
            freeze_time(time_to_freeze='2012-01-14T12:00:00+00:00'),
        ):
            iso_format = get_system_start_datetime().isoformat()
        self.assertEqual(iso_format, '2009-02-13T23:31:30+00:00')

    def test_process_start_datetime(self):
        start_dt = process_start_datetime()
        self.assertIsInstance(start_dt, datetime.datetime)

        with (
            HostSystemMock(),
            freeze_time(time_to_freeze='2012-01-14T12:00:00+00:00'),
        ):
            iso_format = process_start_datetime().isoformat()
        self.assertEqual(iso_format, '2009-02-13T23:31:30+00:00')

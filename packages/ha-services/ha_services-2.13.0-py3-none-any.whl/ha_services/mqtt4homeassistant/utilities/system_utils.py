import datetime
import logging
import os

import psutil


logger = logging.getLogger(__name__)


def get_system_start_datetime() -> datetime.datetime:
    tznow = datetime.datetime.now().astimezone()
    start_dt = datetime.datetime.fromtimestamp(psutil.boot_time(), tz=tznow.tzinfo)
    return start_dt


def process_start_datetime() -> datetime.datetime:
    p = psutil.Process(os.getpid())
    create_time: float = p.create_time()
    tznow = datetime.datetime.now().astimezone()
    start_dt = datetime.datetime.fromtimestamp(create_time, tz=tznow.tzinfo)
    return start_dt


def netstat() -> dict:
    netstat = psutil.net_io_counters(pernic=True)
    filtered = {}
    for interface, statistics in netstat.items():
        if interface == 'lo' or interface.startswith(('veth', 'docker', 'br-')):
            logger.debug(f'Skipping network interface: {interface}')
            continue
        logger.debug(f'Including network interface: {interface}')
        filtered[interface] = statistics
    return filtered


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    print(f'{get_system_start_datetime().isoformat()=}')
    print(f'{process_start_datetime().isoformat()=}')
    print(f'{netstat()=}')

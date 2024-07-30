import os
# from .main import log
from .utils import LogHelper
from .metrics import Metrics
from .wled_client import WLEDClient


log = LogHelper.get_env_logger(__name__)


DEFAULT_WLED_INSTANCE_SCRAPE_INTERVAL_SECONDS = int(os.environ.get(
    'DEFAULT_WLED_INSTANCE_SCRAPE_INTERVAL_SECONDS',
    60))


class ScraperException(Exception):
    pass


class MissingIPListScraperException(ScraperException):
    pass


class Scraper(object):
    @classmethod
    def get_client(cls):
        return Scraper(WLEDClient.get_client())

    @classmethod
    def default_wled_ip(cls):
        # TODO: consolidate env imports
        return os.environ.get('DEFAULT_WLED_IP',
                              "10.0.1.179")

    @classmethod
    def get_default_scrape_interval(cls):
        return int(DEFAULT_WLED_INSTANCE_SCRAPE_INTERVAL_SECONDS)

    @classmethod
    def get_env_wled_ip_list(cls):
        try:
            # TODO: consolidate env imports
            return os.environ['WLED_IP_LIST']
        except KeyError as ke:
            log.error(f"We got no list in the env vars with ke: {ke}")
            return None

    @classmethod
    def parse_env_wled_ip_list(cls):
        raw_ip_list = cls.get_env_wled_ip_list()
        if not raw_ip_list or not len(raw_ip_list):
            return None
        return raw_ip_list.split(',')

    def __init__(self, wled_client):
        self._wled_client = wled_client

    @property
    def wled_client(self):
        return self._wled_client

    def scrape_device_sync(self, device_info, device_state):
        if not device_info:
            return
        if not device_state:
            return
        sync_state = device_state.sync
        log.debug(f"sync_state: {sync_state}")
        Metrics.INSTANCE_SYNC_RECEIVE_STATE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(sync_state.receive or 0)
        Metrics.INSTANCE_SYNC_RECEIVE_GROUPS.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(sync_state.receive_groups or 0)
        Metrics.INSTANCE_SYNC_SEND_STATE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(sync_state.send or 0)
        Metrics.INSTANCE_SYNC_SEND_GROUPS.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(sync_state.send_groups or 0)

    def scrape_device_wifi(self, device_info):
        if not device_info:
            return
        wifi_info = device_info.wifi
        log.debug(f"wifi_info: {wifi_info}")
        Metrics.INSTANCE_WIFI_CHANNEL.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(wifi_info.channel or 0)
        Metrics.INSTANCE_WIFI_RSSI.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(wifi_info.rssi or 0)
        Metrics.INSTANCE_WIFI_SIGNAL.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(wifi_info.signal or 0)

    def scrape_device_info(self, device_info):
        if not device_info:
            return
        log.debug(f"dev_info.version: {device_info.version}")
        log.debug(f"dev_info: {device_info}")

        Metrics.INSTANCE_INFO.labels(
            architecture=device_info.architecture,
            arduino_core_version=device_info.arduino_core_version,
            brand=device_info.brand,
            build=device_info.build,
            ip=device_info.ip,
            mac_address=device_info.mac_address,
            name=device_info.name,
            product=device_info.product,
            version=device_info.version,
        ).set(1)
        Metrics.INSTANCE_FREE_HEAP.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_info.free_heap or 0)

    def scrape_device_state(self, device_info, device_state):
        if not device_info:
            return

        Metrics.INSTANCE_STATE_BRIGHTNESS.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_state.brightness or 0)
        Metrics.INSTANCE_STATE_ON.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_state.on or 0)
        Metrics.INSTANCE_STATE_PLAYLIST_ID.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_state.playlist_id or 0)
        Metrics.INSTANCE_STATE_PRESET_ID.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_state.preset_id or 0)

    async def scrape_default_instance(self):
        device_ip = self.default_wled_ip()
        await self.scrape_instance(device_ip)

    async def scrape_instance(self, device_ip):
        log.debug(f"wled connecting to device_ip: {device_ip}")
        device = await self.wled_client.get_wled_instance_device(
            device_ip)
        log.debug(f"wled got device: {device}")

        try:
            dev_info = device.info
            dev_state = device.state
            self.scrape_device_info(dev_info)
            self.scrape_device_wifi(dev_info)
            self.scrape_device_state(dev_info, dev_state)
            self.scrape_device_sync(dev_info, dev_state)
        except Exception as unexp:
            log.error(f"Unexpected issue for device_ip: {device_ip} "
                      f"with scrape issue unexp: {unexp}")

    async def scrape_all_instances(self):
        wled_ip_list = self.parse_env_wled_ip_list()
        if not wled_ip_list:
            e_m = ('missing wled ip list! must provide '
                   'with env var to use this method')
            log.error(e_m)
            raise MissingIPListScraperException(e_m)
        for device_ip in wled_ip_list:
            log.debug(f"scraping metrics for device_ip: {device_ip}")
            await self.scrape_instance(device_ip)

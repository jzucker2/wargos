from typing import Union

from fastapi import FastAPI
from .version import version

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge


import os
from wled import WLED

from .utils import get_logger


log = get_logger(__name__)


class MetricsLabels(object):
    ARCHITECTURE = 'architecture'
    ARDUINO_CORE_VERSION = 'arduino_core_version'
    BRAND = 'brand'
    BUILD = 'build'
    FREE_HEAP = 'free_heap'
    IP = 'ip'
    MAC_ADDRESS = 'mac_address'
    NAME = 'name'
    PRODUCT = 'product'
    VERSION = 'version'

    @classmethod
    def instance_info_labels(cls):
        return list([
            cls.ARCHITECTURE,
            cls.ARDUINO_CORE_VERSION,
            cls.BRAND,
            cls.BUILD,
            cls.IP,
            cls.MAC_ADDRESS,
            cls.NAME,
            cls.PRODUCT,
            cls.VERSION,
        ])

    @classmethod
    def free_heap_labels(cls):
        return list([
            cls.NAME,
            cls.IP,
        ])

    @classmethod
    def basic_state_labels(cls):
        return list([
            cls.NAME,
            cls.IP,
        ])

    @classmethod
    def basic_udp_sync_labels(cls):
        return list([
            cls.NAME,
            cls.IP,
        ])


class Metrics(object):
    INSTANCE_INFO = Gauge(
        'wargos_wled_instance_basic_info',
        'Details about the WLED instance info, mostly hw and build info',
        MetricsLabels.instance_info_labels())

    INSTANCE_FREE_HEAP = Gauge(
        'wargos_wled_instance_free_heap',
        'The current free heap of the WLED instance (in MB?)',
        MetricsLabels.free_heap_labels())

    INSTANCE_STATE_BRIGHTNESS = Gauge(
        'wargos_wled_instance_state_brightness',
        'The current WLED instance brightness',
        MetricsLabels.basic_state_labels())

    INSTANCE_STATE_ON = Gauge(
        'wargos_wled_instance_state_on',
        'The current WLED instance is on value',
        MetricsLabels.basic_state_labels())

    INSTANCE_STATE_PLAYLIST_ID = Gauge(
        'wargos_wled_instance_state_playlist_id',
        'The current WLED instance playlist_id',
        MetricsLabels.basic_state_labels())

    INSTANCE_STATE_PRESET_ID = Gauge(
        'wargos_wled_instance_state_preset_id',
        'The current WLED instance preset_id',
        MetricsLabels.basic_state_labels())

    INSTANCE_SYNC_RECEIVE_STATE = Gauge(
        'wargos_wled_instance_sync_receive_state',
        'The current state of the WLED instance sync receive setting',
        MetricsLabels.basic_udp_sync_labels()
    )

    INSTANCE_SYNC_SEND_STATE = Gauge(
        'wargos_wled_instance_sync_send_state',
        'The current state of the WLED instance sync send setting',
        MetricsLabels.basic_udp_sync_labels()
    )

    INSTANCE_SYNC_RECEIVE_GROUPS = Gauge(
        'wargos_wled_instance_sync_receive_groups',
        'The current state of the WLED instance sync receive groups',
        MetricsLabels.basic_udp_sync_labels()
    )

    INSTANCE_SYNC_SEND_GROUPS = Gauge(
        'wargos_wled_instance_sync_send_groups',
        'The current state of the WLED instance sync send groups',
        MetricsLabels.basic_udp_sync_labels()
    )


class WLEDClient(object):
    @classmethod
    def get_client(cls):
        return WLEDClient()

    @classmethod
    def default_wled_ip(cls):
        return os.environ.get('DEFAULT_WLED_IP',
                              "10.0.1.179")

    @classmethod
    async def get_wled_instance_device(cls, ip_address):
        log.info(f"wled connecting to ip_address: {ip_address}")
        async with WLED(ip_address) as led:
            device = await led.update()
            log.info(f"wled got device: {device}")

            return device

    @classmethod
    async def simple_wled_test(cls):
        """Don't overcomplicate this one. Simple usage like the dep docs"""
        device_ip = cls.default_wled_ip()
        log.info(f"wled connecting to device_ip: {device_ip}")
        async with WLED(device_ip) as led:
            device = await led.update()
            log.info(f"wled got device: {device}")
            print("device.info.version")
            print(device.info.version)
            print("device.info")
            print(device.info)
            print("device.state")
            print(device.state)

            # Turn strip on, full brightness
            await led.master(on=True, brightness=255)


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
        return os.environ.get('DEFAULT_WLED_IP',
                              "10.0.1.179")

    @classmethod
    def get_env_wled_ip_list(cls):
        try:
            return os.environ['WLED_IP_LIST']
        except KeyError as ke:
            log.info(f"We got no list in the env vars with ke: {ke}")
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
        # TODO: replace the print
        print(sync_state)
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

    async def scrape_default_instance(self):
        device_ip = self.default_wled_ip()
        await self.scrape_instance(device_ip)

    async def scrape_instance(self, device_ip):
        log.info(f"wled connecting to device_ip: {device_ip}")
        device = await self.wled_client.get_wled_instance_device(
            device_ip)
        log.info(f"wled got device: {device}")
        print(device)
        dev_info = device.info
        print("dev_info.version")
        print(dev_info.version)
        print("dev_info")
        print(dev_info)

        Metrics.INSTANCE_INFO.labels(
            architecture=dev_info.architecture,
            arduino_core_version=dev_info.arduino_core_version,
            brand=dev_info.brand,
            build=dev_info.build,
            ip=dev_info.ip,
            mac_address=dev_info.mac_address,
            name=dev_info.name,
            product=dev_info.product,
            version=dev_info.version,
        ).set(1)
        Metrics.INSTANCE_FREE_HEAP.labels(
            ip=dev_info.ip,
            name=dev_info.name,
        ).set(dev_info.free_heap or 0)

        dev_state = device.state
        print("dev_state")
        print(dev_state)

        Metrics.INSTANCE_STATE_BRIGHTNESS.labels(
            ip=dev_info.ip,
            name=dev_info.name,
        ).set(dev_state.brightness or 0)
        Metrics.INSTANCE_STATE_ON.labels(
            ip=dev_info.ip,
            name=dev_info.name,
        ).set(dev_state.on or 0)
        Metrics.INSTANCE_STATE_PLAYLIST_ID.labels(
            ip=dev_info.ip,
            name=dev_info.name,
        ).set(dev_state.playlist_id or 0)
        Metrics.INSTANCE_STATE_PRESET_ID.labels(
            ip=dev_info.ip,
            name=dev_info.name,
        ).set(dev_state.preset_id or 0)
        try:
            self.scrape_device_sync(dev_info, dev_state)
        except Exception as unexp:
            print(f"Unexpected scrape sync unexp: {unexp}")

    async def scrape_all_instances(self):
        wled_ip_list = self.parse_env_wled_ip_list()
        if not wled_ip_list:
            e_m = ('missing wled ip list! must provide '
                   'with env var to use this method')
            raise MissingIPListScraperException(e_m)
        for device_ip in wled_ip_list:
            await self.scrape_instance(device_ip)


app = FastAPI()


Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/healthz")
def healthcheck():
    return {
        "message": "healthy",
        "version": version,
    }


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# real stuff here


@app.get("/test")
async def simple_test():
    await WLEDClient.simple_wled_test()
    return {"message": "Hello World"}


@app.get("/prometheus/default")
async def prometheus_default():
    await Scraper.get_client().scrape_default_instance()
    return {"message": "Hello World"}


@app.get("/prometheus/all")
async def prometheus_scrape_all():
    await Scraper.get_client().scrape_all_instances()
    return {"message": "Hello World"}

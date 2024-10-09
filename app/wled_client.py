import os
from wled import WLED, WLEDReleases
from .utils import LogHelper
from .metrics import Metrics


log = LogHelper.get_env_logger(__name__)


class WLEDClient(object):
    @classmethod
    def get_client(cls, session=None):
        return cls(session=session)

    @classmethod
    def default_wled_ip(cls):
        return os.environ.get('DEFAULT_WLED_IP',
                              "10.0.1.179")

    def __init__(self, session=None):
        super().__init__()
        self._session = session

    @property
    def session(self):
        return self._session

    def _connecting_device(self, ip_address):
        if self.session:
            return WLED(host=ip_address, session=self.session)
        return WLED(host=ip_address)

    def _connecting_releases(self):
        if self.session:
            return WLEDReleases(session=self.session)
        return WLEDReleases()

    async def get_wled_instance_device(self, ip_address):
        log.debug(f"wled connecting to ip_address: {ip_address}")
        with Metrics.WLED_CLIENT_CONNECT_EXCEPTIONS.labels(
            ip=ip_address,
        ).count_exceptions():
            with Metrics.WLED_CLIENT_CONNECT_TIME.labels(
                ip=ip_address,
            ).time():
                async with self._connecting_device(ip_address) as led:
                    device = await led.update()
                    log.debug(f"wled got device: {device}")

                    return device

    async def simple_wled_test(self):
        """Don't overcomplicate this one. Simple usage like the dep docs"""
        device_ip = self.default_wled_ip()
        Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER.labels(
            ip=device_ip,
        ).inc()
        log.info(f"wled connecting to device_ip: {device_ip}")
        async with self._connecting_device(device_ip) as led:
            device = await led.update()
            log.info(f"wled got device: {device}")
            log.info(f"device.info.version => {device.info.version}")
            log.info(f"device.info => {device.info}")
            log.info(f"device.state => {device.state}")

            # Turn strip on, full brightness
            await led.master(on=True, brightness=255)

    async def simple_wled_releases_test(self):
        log.debug(f"simple wled releases test")
        async with self._connecting_releases() as releases:
            latest = await releases.releases()
            log.info(f"Latest stable version: {latest.stable}")
            log.info(f"Latest beta version: {latest.beta}")

    async def get_wled_latest_releases(self):
        log.debug(f"wled connecting to releases")
        with Metrics.WLED_RELEASES_CONNECT_EXCEPTIONS.count_exceptions():
            with Metrics.WLED_RELEASES_CONNECT_TIME.time():
                async with self._connecting_releases() as releases:
                    latest = await releases.releases()
                    log.debug(f"Latest stable version: {latest.stable}")
                    log.debug(f"Latest beta version: {latest.beta}")
                    return latest

import json
import os
from datetime import datetime
from pathlib import Path

import aiohttp

from .metrics import Metrics
from .utils import LogHelper
from .version import version
from .wled_client import WLEDClient

log = LogHelper.get_env_logger(__name__)


DEFAULT_WLED_INSTANCE_SCRAPE_INTERVAL_SECONDS = int(
    os.environ.get("DEFAULT_WLED_INSTANCE_SCRAPE_INTERVAL_SECONDS", 60)
)
DEFAULT_WLED_FIRST_WAIT_SECONDS = int(
    os.environ.get("DEFAULT_WLED_FIRST_WAIT_SECONDS", 30)
)


class ScraperException(Exception):
    pass


class MissingIPListScraperException(ScraperException):
    pass


class ConfigBackupException(ScraperException):
    pass


class Scraper(object):
    @classmethod
    def get_client(cls):
        return cls(WLEDClient.get_client())

    def default_wled_ip(self):
        return self.wled_client.default_wled_ip()

    @classmethod
    def get_default_scrape_interval(cls):
        return int(DEFAULT_WLED_INSTANCE_SCRAPE_INTERVAL_SECONDS)

    @classmethod
    def get_default_wait_first_interval(cls):
        return int(DEFAULT_WLED_FIRST_WAIT_SECONDS)

    @classmethod
    def should_scrape_releases(cls):
        """Check if releases should be scraped based on environment variable"""
        return os.environ.get("ENABLE_RELEASE_CHECK", "true").lower() in (
            "true",
            "1",
            "yes",
            "on",
        )

    @classmethod
    def get_env_wled_ip_list(cls):
        try:
            # TODO: consolidate env imports
            return os.environ["WLED_IP_LIST"]
        except KeyError as ke:
            log.error(f"We got no list in the env vars with ke: {ke}")
            return None

    @classmethod
    def parse_env_wled_ip_list(cls):
        raw_ip_list = cls.get_env_wled_ip_list()
        if not raw_ip_list or not len(raw_ip_list):
            return None
        return raw_ip_list.split(",")

    @classmethod
    def get_config_backup_dir(cls):
        """Get the config backup directory from environment variable"""
        return os.environ.get("CONFIG_BACKUP_DIR", "/backups/")

    def __init__(self, wled_client):
        self._wled_client = wled_client

    @property
    def wled_client(self):
        return self._wled_client

    async def backup_config_from_instance(self, device_ip, backup_dir=None):
        """Backup config from a single WLED instance"""
        if backup_dir is None:
            backup_dir = self.get_config_backup_dir()

        # Create backup directory and IP subdirectory if they don't exist
        ip_backup_dir = Path(backup_dir) / device_ip / "configs"
        ip_backup_dir.mkdir(parents=True, exist_ok=True)

        config_url = f"http://{device_ip}/cfg.json"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{device_ip}_{timestamp}_configs.json"
        filepath = ip_backup_dir / filename

        log.info(f"Backing up config from {device_ip} to {filepath}")

        # Track operation start time for metrics
        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config_url, timeout=10) as response:
                    if response.status == 200:
                        config_data = await response.json()

                        # Add metadata to the config
                        config_data["_backup_metadata"] = {
                            "backup_timestamp": datetime.now().isoformat(),
                            "device_ip": device_ip,
                            "backup_source": "wargos",
                        }

                        # Write config to file
                        with open(filepath, "w") as f:
                            json.dump(config_data, f, indent=2)

                        # Get file size for metrics
                        file_size = filepath.stat().st_size

                        # Update metrics
                        duration = (
                            datetime.now() - start_time
                        ).total_seconds()
                        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                            operation_type="single_backup",
                            device_ip=device_ip,
                            status="success",
                        ).inc()
                        Metrics.CONFIG_BACKUP_OPERATION_DURATION.labels(
                            operation_type="single_backup", device_ip=device_ip
                        ).observe(duration)
                        Metrics.CONFIG_BACKUP_FILES_CREATED.labels(
                            device_ip=device_ip
                        ).inc()
                        Metrics.CONFIG_BACKUP_FILE_SIZE_BYTES.labels(
                            device_ip=device_ip
                        ).set(file_size)

                        log.info(
                            f"Successfully backed up config from {device_ip} to {filepath}"
                        )
                        return {
                            "device_ip": device_ip,
                            "filepath": str(filepath),
                            "timestamp": timestamp,
                            "status": "success",
                        }
                    else:
                        # Track HTTP errors
                        Metrics.CONFIG_BACKUP_HTTP_ERRORS.labels(
                            device_ip=device_ip,
                            http_status_code=str(response.status),
                        ).inc()
                        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                            operation_type="single_backup",
                            device_ip=device_ip,
                            status="error",
                        ).inc()

                        error_msg = f"Failed to fetch config from {device_ip}: HTTP {response.status}"
                        log.error(error_msg)
                        return {
                            "device_ip": device_ip,
                            "filepath": None,
                            "timestamp": timestamp,
                            "status": "error",
                            "error": error_msg,
                        }
        except Exception as e:
            # Track exceptions
            exception_type = type(e).__name__
            Metrics.CONFIG_BACKUP_OPERATION_EXCEPTIONS.labels(
                operation_type="single_backup",
                device_ip=device_ip,
                exception_type=exception_type,
            ).inc()
            Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                operation_type="single_backup",
                device_ip=device_ip,
                status="error",
            ).inc()

            # Track connection errors specifically
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                Metrics.CONFIG_BACKUP_CONNECTION_ERRORS.labels(
                    device_ip=device_ip, error_type=exception_type
                ).inc()

            error_msg = f"Error backing up config from {device_ip}: {str(e)}"
            log.error(error_msg)
            return {
                "device_ip": device_ip,
                "filepath": None,
                "timestamp": timestamp,
                "status": "error",
                "error": error_msg,
            }

    async def backup_presets_from_instance(self, device_ip, backup_dir=None):
        """Backup presets from a single WLED instance"""
        if backup_dir is None:
            backup_dir = self.get_config_backup_dir()

        # Create backup directory and IP subdirectory if they don't exist
        ip_backup_dir = Path(backup_dir) / device_ip / "presets"
        ip_backup_dir.mkdir(parents=True, exist_ok=True)

        presets_url = f"http://{device_ip}/presets.json"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{device_ip}_{timestamp}_presets.json"
        filepath = ip_backup_dir / filename

        log.info(f"Backing up presets from {device_ip} to {filepath}")

        # Track operation start time for metrics
        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(presets_url, timeout=10) as response:
                    if response.status == 200:
                        presets_data = await response.json()

                        # Check for empty presets (special case)
                        if presets_data == {"0": {}}:
                            # Update metrics for empty presets
                            duration = (
                                datetime.now() - start_time
                            ).total_seconds()
                            Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                                operation_type="single_preset_backup",
                                device_ip=device_ip,
                                status="empty_presets",
                            ).inc()
                            Metrics.CONFIG_BACKUP_OPERATION_DURATION.labels(
                                operation_type="single_preset_backup",
                                device_ip=device_ip,
                            ).observe(duration)

                            log.info(
                                f"Empty presets detected for {device_ip}, skipping file creation"
                            )
                            return {
                                "device_ip": device_ip,
                                "filepath": None,
                                "timestamp": timestamp,
                                "status": "empty_presets",
                                "message": "No presets to backup",
                            }

                        # Add metadata to the presets
                        presets_data["_backup_metadata"] = {
                            "backup_timestamp": datetime.now().isoformat(),
                            "device_ip": device_ip,
                            "backup_source": "wargos",
                        }

                        # Write presets to file
                        with open(filepath, "w") as f:
                            json.dump(presets_data, f, indent=2)

                        # Get file size for metrics
                        file_size = filepath.stat().st_size

                        # Update metrics
                        duration = (
                            datetime.now() - start_time
                        ).total_seconds()
                        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                            operation_type="single_preset_backup",
                            device_ip=device_ip,
                            status="success",
                        ).inc()
                        Metrics.CONFIG_BACKUP_OPERATION_DURATION.labels(
                            operation_type="single_preset_backup",
                            device_ip=device_ip,
                        ).observe(duration)
                        Metrics.CONFIG_BACKUP_FILES_CREATED.labels(
                            device_ip=device_ip
                        ).inc()
                        Metrics.CONFIG_BACKUP_FILE_SIZE_BYTES.labels(
                            device_ip=device_ip
                        ).set(file_size)

                        log.info(
                            f"Successfully backed up presets from {device_ip} to {filepath}"
                        )
                        return {
                            "device_ip": device_ip,
                            "filepath": str(filepath),
                            "timestamp": timestamp,
                            "status": "success",
                        }
                    else:
                        # Track HTTP errors
                        Metrics.CONFIG_BACKUP_HTTP_ERRORS.labels(
                            device_ip=device_ip,
                            http_status_code=str(response.status),
                        ).inc()
                        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                            operation_type="single_preset_backup",
                            device_ip=device_ip,
                            status="error",
                        ).inc()

                        error_msg = f"Failed to fetch presets from {device_ip}: HTTP {response.status}"
                        log.error(error_msg)
                        return {
                            "device_ip": device_ip,
                            "filepath": None,
                            "timestamp": timestamp,
                            "status": "error",
                            "error": error_msg,
                        }
        except Exception as e:
            # Track exceptions
            exception_type = type(e).__name__
            Metrics.CONFIG_BACKUP_OPERATION_EXCEPTIONS.labels(
                operation_type="single_preset_backup",
                device_ip=device_ip,
                exception_type=exception_type,
            ).inc()
            Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                operation_type="single_preset_backup",
                device_ip=device_ip,
                status="error",
            ).inc()

            # Track connection errors specifically
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                Metrics.CONFIG_BACKUP_CONNECTION_ERRORS.labels(
                    device_ip=device_ip, error_type=exception_type
                ).inc()

            error_msg = f"Error backing up presets from {device_ip}: {str(e)}"
            log.error(error_msg)
            return {
                "device_ip": device_ip,
                "filepath": None,
                "timestamp": timestamp,
                "status": "error",
                "error": error_msg,
            }

    async def backup_configs_from_all_instances(self, backup_dir=None):
        """Backup configs from all WLED instances"""
        wled_ip_list = self.parse_env_wled_ip_list()
        if not wled_ip_list:
            e_m = "missing wled ip list! must provide with env var to use this method"
            log.error(e_m)
            raise MissingIPListScraperException(e_m)

        # Track bulk operation start time
        start_time = datetime.now()
        successful_backups = 0
        failed_backups = 0

        results = []
        for device_ip in wled_ip_list:
            log.debug(f"backing up config for device_ip: {device_ip}")
            try:
                result = await self.backup_config_from_instance(
                    device_ip, backup_dir
                )
                results.append(result)

                # Track success/failure for bulk operation
                if result["status"] == "success":
                    successful_backups += 1
                else:
                    failed_backups += 1

            except Exception as unexp:
                failed_backups += 1
                u_m = f"Config backup failed for device_ip: {device_ip} got unexp: {unexp}"
                log.error(u_m)
                results.append(
                    {
                        "device_ip": device_ip,
                        "filepath": None,
                        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                        "status": "error",
                        "error": str(unexp),
                    }
                )

        # Update bulk operation metrics
        duration = (datetime.now() - start_time).total_seconds()
        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
            operation_type="bulk_backup", device_ip="all", status="completed"
        ).inc()
        Metrics.CONFIG_BACKUP_OPERATION_DURATION.labels(
            operation_type="bulk_backup", device_ip="all"
        ).observe(duration)

        # Track individual results
        for result in results:
            if result["status"] == "success":
                Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                    operation_type="bulk_backup_success",
                    device_ip=result["device_ip"],
                    status="success",
                ).inc()
            else:
                Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                    operation_type="bulk_backup_failed",
                    device_ip=result["device_ip"],
                    status="error",
                ).inc()

        return results

    async def backup_presets_from_all_instances(self, backup_dir=None):
        """Backup presets from all WLED instances"""
        wled_ip_list = self.parse_env_wled_ip_list()
        if not wled_ip_list:
            e_m = "missing wled ip list! must provide with env var to use this method"
            log.error(e_m)
            raise MissingIPListScraperException(e_m)

        # Track bulk operation start time
        start_time = datetime.now()
        successful_backups = 0
        failed_backups = 0

        results = []
        for device_ip in wled_ip_list:
            log.debug(f"backing up presets for device_ip: {device_ip}")
            try:
                result = await self.backup_presets_from_instance(
                    device_ip, backup_dir
                )
                results.append(result)

                # Track success/failure for bulk operation
                if result["status"] == "success":
                    successful_backups += 1
                else:
                    failed_backups += 1

            except Exception as unexp:
                failed_backups += 1
                u_m = f"Preset backup failed for device_ip: {device_ip} got unexp: {unexp}"
                log.error(u_m)
                results.append(
                    {
                        "device_ip": device_ip,
                        "filepath": None,
                        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                        "status": "error",
                        "error": str(unexp),
                    }
                )

        # Update bulk operation metrics
        duration = (datetime.now() - start_time).total_seconds()
        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
            operation_type="bulk_preset_backup",
            device_ip="all",
            status="completed",
        ).inc()
        Metrics.CONFIG_BACKUP_OPERATION_DURATION.labels(
            operation_type="bulk_preset_backup", device_ip="all"
        ).observe(duration)

        # Track individual results
        for result in results:
            if result["status"] == "success":
                Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                    operation_type="bulk_preset_backup_success",
                    device_ip=result["device_ip"],
                    status="success",
                ).inc()
            else:
                Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                    operation_type="bulk_preset_backup_failed",
                    device_ip=result["device_ip"],
                    status="error",
                ).inc()

        return results

    async def backup_all_from_all_instances(self, backup_dir=None):
        """Backup both configs and presets from all WLED instances"""
        wled_ip_list = self.parse_env_wled_ip_list()
        if not wled_ip_list:
            e_m = "missing wled ip list! must provide with env var to use this method"
            log.error(e_m)
            raise MissingIPListScraperException(e_m)

        # Track bulk operation start time
        start_time = datetime.now()

        config_results = await self.backup_configs_from_all_instances(
            backup_dir
        )
        preset_results = await self.backup_presets_from_all_instances(
            backup_dir
        )

        # Update bulk operation metrics
        duration = (datetime.now() - start_time).total_seconds()
        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
            operation_type="bulk_all_backup",
            device_ip="all",
            status="completed",
        ).inc()
        Metrics.CONFIG_BACKUP_OPERATION_DURATION.labels(
            operation_type="bulk_all_backup", device_ip="all"
        ).observe(duration)

        return {
            "configs": config_results,
            "presets": preset_results,
            "total_devices": len(wled_ip_list),
        }

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
        Metrics.INSTANCE_WIFI_BSSID.labels(
            ip=device_info.ip,
            name=device_info.name,
            bssid=wifi_info.bssid,
        ).set(1)

    def scrape_device_presets(self, device_info, device):
        if not device_info:
            return
        presets = device.presets
        preset_info_list = list(presets.values())
        preset_count = len(preset_info_list)
        log.debug(f"found preset_count: {preset_count} => presets: {presets}")
        Metrics.INSTANCE_PRESET_COUNT_VALUE.labels(
            name=device_info.name,
            ip=device_info.ip,
        ).set(preset_count or 0)
        for preset_info in preset_info_list:
            log.debug(f"found preset_info: {preset_info}")
            preset_id = preset_info.preset_id
            preset_name = preset_info.name
            final_quick_label = preset_info.quick_label or "missing"
            Metrics.INSTANCE_PRESET_IS_ON_VALUE.labels(
                name=device_info.name,
                ip=device_info.ip,
                preset_id=preset_id,
                preset_name=preset_name,
            ).set(preset_info.on or 0)
            Metrics.INSTANCE_PRESET_TRANSITION_VALUE.labels(
                name=device_info.name,
                ip=device_info.ip,
                preset_id=preset_id,
                preset_name=preset_name,
            ).set(preset_info.transition or 0)
            Metrics.INSTANCE_PRESET_QUICK_LABEL_INFO.labels(
                name=device_info.name,
                ip=device_info.ip,
                preset_id=preset_id,
                preset_name=preset_name,
                preset_quick_label=final_quick_label,
            ).set(1)

    def scrape_uptime(self, device_info):
        Metrics.INSTANCE_UPTIME_SECONDS.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_info.uptime.total_seconds() or 0)

    def scrape_websocket_clients(self, device_info):
        Metrics.INSTANCE_WEBSOCKET_CLIENTS.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_info.websocket or 0)

    def scrape_udp_port(self, device_info):
        Metrics.INSTANCE_UDP_PORT.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_info.udp_port or 0)

    def scrape_state_nightlight(self, device_info, device_state):
        dev_nightlight = device_state.nightlight
        log.debug(f"got dev_nightlight: {dev_nightlight}")
        Metrics.INSTANCE_NIGHTLIGHT_DURATION_MINUTES.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_nightlight.duration or 0)
        Metrics.INSTANCE_NIGHTLIGHT_ON_VALUE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_nightlight.on or 0)
        Metrics.INSTANCE_NIGHTLIGHT_TARGET_BRIGHTNESS_VALUE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_nightlight.target_brightness or 0)

    def _scrape_single_priority_color(
        self, device_info, segment_name, color_priority, colors
    ):
        if not colors:
            return
        color_position = 0
        for color_value in colors:
            log.debug(
                f"color_priority ({color_priority}) ==> at "
                f"color_position: {color_position} "
                f"color_value: {color_value}"
            )
            Metrics.INSTANCE_SEGMENT_COLOR_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
                color_priority=color_priority,
                color_tuple_position=color_position,
            ).set(color_value)
            color_position += 1

    def scrape_state_segment_colors(
        self, device_info, segment_name, segment_info
    ):
        dev_colors = segment_info.color
        log.debug(f"got dev_colors: {dev_colors}")
        if not dev_colors:
            return
        primary_colors = dev_colors.primary
        self._scrape_single_priority_color(
            device_info, segment_name, "primary", primary_colors
        )
        secondary_colors = dev_colors.secondary
        self._scrape_single_priority_color(
            device_info, segment_name, "secondary", secondary_colors
        )
        tertiary_colors = dev_colors.tertiary
        self._scrape_single_priority_color(
            device_info, segment_name, "tertiary", tertiary_colors
        )

    def scrape_state_segments(self, device_info, device_state):
        dev_segments_list = device_state.segments
        log.debug(f"got dev_segments_list: {dev_segments_list}")
        for segment_name, segment_info in dev_segments_list.items():
            Metrics.INSTANCE_SEGMENT_BRIGHTNESS_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.brightness or 0)
            Metrics.INSTANCE_SEGMENT_CLONES_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.clones or 0)
            Metrics.INSTANCE_SEGMENT_EFFECT_ID_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.effect_id or 0)
            Metrics.INSTANCE_SEGMENT_INTENSITY_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.intensity or 0)
            Metrics.INSTANCE_SEGMENT_LENGTH_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.length or 0)
            Metrics.INSTANCE_SEGMENT_ON_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.on or 0)
            Metrics.INSTANCE_SEGMENT_PALETTE_ID_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.palette_id or 0)
            Metrics.INSTANCE_SEGMENT_REVERSE_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.reverse or 0)
            Metrics.INSTANCE_SEGMENT_SEGMENT_ID_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.segment_id or 0)
            Metrics.INSTANCE_SEGMENT_SELECTED_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.selected or 0)
            Metrics.INSTANCE_SEGMENT_SPEED_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.speed or 0)
            Metrics.INSTANCE_SEGMENT_CCT_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.cct or 0)
            Metrics.INSTANCE_SEGMENT_START_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.start or 0)
            Metrics.INSTANCE_SEGMENT_STOP_VALUE.labels(
                ip=device_info.ip,
                name=device_info.name,
                segment=segment_name,
            ).set(segment_info.stop or 0)
            log.debug(
                f"Now try and scrape colors "
                f"from segment_name: {segment_name}"
            )
            self.scrape_state_segment_colors(
                device_info, segment_name, segment_info
            )

    def scrape_info_filesystem(self, device_info):
        dev_fs = device_info.filesystem
        log.debug(f"got dev_fs: {dev_fs}")
        Metrics.INSTANCE_FILESYSTEM_SPACE_TOTAL.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_fs.total or 0)
        Metrics.INSTANCE_FILESYSTEM_SPACE_USED.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_fs.used or 0)

    def scrape_info_leds(self, device_info):
        dev_leds = device_info.leds
        log.debug(f"got dev_leds: {dev_leds}")
        Metrics.INSTANCE_LED_COUNT_VALUE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_leds.count or 0)
        Metrics.INSTANCE_LED_FPS_VALUE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_leds.fps or 0)
        Metrics.INSTANCE_LED_MAX_SEGMENTS.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_leds.max_segments or 0)
        Metrics.INSTANCE_LED_MAX_POWER.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_leds.max_power or 0)
        Metrics.INSTANCE_LED_CURRENT_POWER.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(dev_leds.power or 0)

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
            version=str(device_info.version),
        ).set(1)
        Metrics.INSTANCE_FREE_HEAP.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_info.free_heap or 0)
        Metrics.INSTANCE_PALETTE_COUNT_VALUE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_info.palette_count or 0)
        Metrics.INSTANCE_EFFECT_COUNT_VALUE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_info.effect_count or 0)
        Metrics.INSTANCE_LIVE_STATE.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_info.live or 0)

    def scrape_device_state(self, device_info, device_state):
        if not device_info:
            return

        Metrics.INSTANCE_STATE_BRIGHTNESS.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_state.brightness or 0)
        Metrics.INSTANCE_STATE_TRANSITION.labels(
            ip=device_info.ip,
            name=device_info.name,
        ).set(device_state.transition or 0)
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
        with Metrics.WLED_SCRAPER_SCRAPE_INSTANCE_EXCEPTIONS.labels(
            ip=device_ip,
        ).count_exceptions():
            with Metrics.WLED_SCRAPER_SCRAPE_INSTANCE_TIME.labels(
                ip=device_ip,
            ).time():
                log.debug(f"wled connecting to device_ip: {device_ip}")
                Metrics.WLED_INSTANCE_SCRAPE_EVENTS_COUNTER.labels(
                    ip=device_ip,
                    # name=dev_info.name,
                    scrape_event="started",
                ).inc()
                # Want to set this _before_ trying to connect
                # because timeouts haven't been configured yet
                Metrics.WLED_INSTANCE_ONLINE.labels(
                    ip=device_ip,
                    # name=dev_info.name,
                ).set(0)
                device = await self.wled_client.get_wled_instance_device(
                    device_ip
                )
                Metrics.WLED_INSTANCE_SCRAPE_EVENTS_COUNTER.labels(
                    ip=device_ip,
                    # name=dev_info.name,
                    scrape_event="connected",
                ).inc()
                log.debug(f"wled got device: {device}")

                try:
                    dev_info = device.info
                    dev_state = device.state
                    self.scrape_device_presets(dev_info, device)
                    self.scrape_device_info(dev_info)
                    self.scrape_uptime(dev_info)
                    self.scrape_websocket_clients(dev_info)
                    self.scrape_udp_port(dev_info)
                    self.scrape_info_leds(dev_info)
                    self.scrape_info_filesystem(dev_info)
                    self.scrape_device_wifi(dev_info)
                    self.scrape_device_state(dev_info, dev_state)
                    self.scrape_device_sync(dev_info, dev_state)
                    self.scrape_state_nightlight(dev_info, dev_state)
                    self.scrape_state_segments(dev_info, dev_state)
                except Exception as unexp:
                    log.error(
                        f"Unexpected issue for device_ip: {device_ip} "
                        f"with scrape issue unexp: {unexp} with "
                        f"type(unexp): {type(unexp)}"
                    )
                    exc_class = str(type(unexp).__name__)
                    log.debug(
                        f"Unexpected exception unexp: {unexp} with "
                        f"type(unexp): {type(unexp)} has exc_class: "
                        f"{exc_class}"
                    )
                    Metrics.WLED_SCRAPER_SCRAPE_INSTANCE_BY_TYPE_EXCEPTIONS.labels(  # noqa: E501
                        ip=device_ip,
                        exception_class=exc_class,
                    ).inc()
                    Metrics.WLED_INSTANCE_SCRAPE_EVENTS_COUNTER.labels(
                        ip=device_ip,
                        # name=dev_info.name,
                        scrape_event="failed",
                    ).inc()
                    Metrics.WLED_INSTANCE_ONLINE.labels(
                        ip=device_ip,
                        # name=dev_info.name,
                    ).set(0)
                else:
                    Metrics.WLED_INSTANCE_SCRAPE_EVENTS_COUNTER.labels(
                        ip=device_ip,
                        # name=dev_info.name,
                        scrape_event="succeeded",
                    ).inc()
                    Metrics.WLED_INSTANCE_ONLINE.labels(
                        ip=device_ip,
                        # name=dev_info.name,
                    ).set(1)

    def scrape_self(self):
        with Metrics.WLED_SCRAPER_SCRAPE_SELF_EXCEPTIONS.count_exceptions():
            with Metrics.WLED_SCRAPER_SCRAPE_SELF_TIME.time():
                current_version = version
                Metrics.WARGOS_INSTANCE_INFO.labels(
                    version=current_version,
                ).set(1)

    async def scrape_all_instances(self):
        with Metrics.WLED_SCRAPER_SCRAPE_ALL_EXCEPTIONS.count_exceptions():
            with Metrics.WLED_SCRAPER_SCRAPE_ALL_TIME.time():
                wled_ip_list = self.parse_env_wled_ip_list()
                if not wled_ip_list:
                    e_m = (
                        "missing wled ip list! must provide "
                        "with env var to use this method"
                    )
                    log.error(e_m)
                    raise MissingIPListScraperException(e_m)
                for device_ip in wled_ip_list:
                    log.debug(f"scraping metrics for device_ip: {device_ip}")
                    try:
                        await self.scrape_instance(device_ip)
                    # TODO: why does it throw up here and not within function?
                    except Exception as unexp:
                        u_m = (
                            f"Scrape all device_ip: {device_ip} "
                            f"got unexp: {unexp}"
                        )
                        log.error(u_m)

    async def scrape_releases(self):
        with Metrics.SCRAPER_SCRAPE_RELEASES_EXCEPTIONS.count_exceptions():
            with Metrics.SCRAPER_SCRAPE_RELEASES_TIME.time():
                latest = await self.wled_client.get_wled_latest_releases()
                Metrics.WLED_RELEASES_INFO.labels(
                    stable=str(latest.stable),
                    beta=str(latest.beta),
                ).set(1)

    async def perform_full_scrape(self):
        # first scrape self info for this app
        log.debug("perform_full_scrape")
        with Metrics.SCRAPER_FULL_SCRAPE_EXCEPTIONS.count_exceptions():
            with Metrics.SCRAPER_FULL_SCRAPE_TIME.time():
                self.scrape_self()
                log.debug("done with scrape self, next all wled instances")
                # then scrape all wled instances
                await self.scrape_all_instances()
                log.debug("done scraping all wled instances, now releases")
                if self.should_scrape_releases():
                    log.debug("release checking enabled - scraping releases")
                    await self.scrape_releases()
                else:
                    log.debug("release checking disabled - skipping releases")
                log.debug("done with perform_full_scrape")

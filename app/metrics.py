from enum import Enum

from prometheus_client import Counter, Gauge, Summary


class MetricsLabels(Enum):
    ARCHITECTURE = "architecture"
    ARDUINO_CORE_VERSION = "arduino_core_version"
    BRAND = "brand"
    BUILD = "build"
    FREE_HEAP = "free_heap"
    IP = "ip"
    MAC_ADDRESS = "mac_address"
    NAME = "name"
    PRODUCT = "product"
    VERSION = "version"
    SEGMENT = "segment"
    BSSID = "bssid"
    EXCEPTION_CLASS = "exception_class"
    COLOR_PRIORITY = "color_priority"
    COLOR_TUPLE_POSITION = "color_tuple_position"
    SCRAPE_EVENT = "scrape_event"
    PRESET_ID = "preset_id"
    PRESET_NAME = "preset_name"
    PRESET_QUICK_LABEL = "preset_quick_label"
    STABLE = "stable"
    BETA = "beta"
    PID = "pid"

    @classmethod
    def releases_labels(cls):
        return list(
            [
                cls.STABLE.value,
                cls.BETA.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def wargos_instance_info_labels(cls):
        return list(
            [
                cls.VERSION.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def instance_info_labels(cls):
        return list(
            [
                cls.ARCHITECTURE.value,
                cls.ARDUINO_CORE_VERSION.value,
                cls.BRAND.value,
                cls.BUILD.value,
                cls.IP.value,
                cls.MAC_ADDRESS.value,
                cls.NAME.value,
                cls.PRODUCT.value,
                cls.VERSION.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def basic_info_labels(cls):
        return list(
            [
                cls.NAME.value,
                cls.IP.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def scrape_events_labels(cls):
        return list(
            [
                cls.IP.value,
                cls.SCRAPE_EVENT.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def wifi_bssid_labels(cls):
        return list(
            [
                cls.NAME.value,
                cls.IP.value,
                cls.BSSID.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def basic_segment_labels(cls):
        return list(
            [
                cls.NAME.value,
                cls.IP.value,
                cls.SEGMENT.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def segment_color_labels(cls):
        return list(
            [
                cls.NAME.value,
                cls.IP.value,
                cls.SEGMENT.value,
                cls.COLOR_PRIORITY.value,
                cls.COLOR_TUPLE_POSITION.value,
            ]
        )

    @classmethod
    def basic_client_labels(cls):
        return list(
            [
                cls.IP.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def basic_online_labels(cls):
        return list(
            [
                cls.IP.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def basic_instance_scraper_labels(cls):
        return list(
            [
                cls.IP.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def instance_scraper_exception_labels(cls):
        return list(
            [
                cls.IP.value,
                cls.EXCEPTION_CLASS.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def basic_state_labels(cls):
        return list(
            [
                cls.NAME.value,
                cls.IP.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def basic_udp_sync_labels(cls):
        return list(
            [
                cls.NAME.value,
                cls.IP.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def basic_preset_labels(cls):
        return list(
            [
                cls.NAME.value,
                cls.IP.value,
                cls.PRESET_ID.value,
                cls.PRESET_NAME.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def preset_quick_label_labels(cls):
        return list(
            [
                cls.NAME.value,
                cls.IP.value,
                cls.PRESET_ID.value,
                cls.PRESET_NAME.value,
                cls.PRESET_QUICK_LABEL.value,
                cls.PID.value,
            ]
        )

    @classmethod
    def backup_operations_labels(cls):
        return list(
            [
                "operation_type",
                "device_ip",
                "status",
                "backup_type",
                cls.PID.value,
            ]
        )

    @classmethod
    def backup_operation_duration_labels(cls):
        return list(
            [
                "operation_type",
                "device_ip",
                "backup_type",
                cls.PID.value,
            ]
        )

    @classmethod
    def backup_operation_exceptions_labels(cls):
        return list(
            [
                "operation_type",
                "device_ip",
                "exception_type",
                "backup_type",
                cls.PID.value,
            ]
        )

    @classmethod
    def backup_files_created_labels(cls):
        return list(
            [
                "device_ip",
                "backup_type",
                cls.PID.value,
            ]
        )

    @classmethod
    def backup_file_size_labels(cls):
        return list(
            [
                "device_ip",
                "backup_type",
                cls.PID.value,
            ]
        )

    @classmethod
    def backup_http_errors_labels(cls):
        return list(
            [
                "device_ip",
                "http_status_code",
                "backup_type",
                cls.PID.value,
            ]
        )

    @classmethod
    def backup_connection_errors_labels(cls):
        return list(
            [
                "device_ip",
                "error_type",
                "backup_type",
                cls.PID.value,
            ]
        )


class Metrics(object):
    WARGOS_INSTANCE_INFO = Gauge(
        "wargos_instance_info",
        "Details about the actual wargos scraper instance (this app)",
        MetricsLabels.wargos_instance_info_labels(),
    )

    WLED_CLIENT_SIMPLE_TEST_COUNTER = Counter(
        "wargos_wled_client_simple_test_total",
        "Count of times the simple WLED client test is run",
        MetricsLabels.basic_client_labels(),
    )

    WLED_CLIENT_CONNECT_EXCEPTIONS = Counter(
        "wargos_wled_client_connect_exceptions_total",
        "Counts any exceptions attempting to connect to a WLED instance",
        MetricsLabels.basic_client_labels(),
    )

    WLED_CLIENT_CONNECT_TIME = Summary(
        "wargos_wled_client_connect_time_seconds",
        "Tracks the timing for a wled instance connection",
        MetricsLabels.basic_client_labels(),
    )

    WLED_RELEASES_CONNECT_EXCEPTIONS = Counter(
        "wargos_wled_releases_connect_exceptions_total",
        "Counts any exceptions attempting to connect to a WLED releases check",
    )

    WLED_RELEASES_CONNECT_TIME = Summary(
        "wargos_wled_releases_connect_time_seconds",
        "Tracks the timing for a wled releases check connection",
    )

    SCRAPER_SCRAPE_RELEASES_EXCEPTIONS = Counter(
        "wargos_wled_scraper_scrape_releases_exceptions_total",
        "Counts any exceptions attempting to scrape releases",
    )

    SCRAPER_SCRAPE_RELEASES_TIME = Summary(
        "wargos_wled_scraper_scrape_releases_time_seconds",
        "Tracks the timing for scraping releases",
    )

    WLED_RELEASES_INFO = Gauge(
        "wargos_wled_releases_basic_info",
        "Details about the WLED latest releases info",
        MetricsLabels.releases_labels(),
    )

    SCRAPER_FULL_SCRAPE_EXCEPTIONS = Counter(
        "wargos_wled_scraper_scrape_full_scrape_exceptions_total",
        "Counts any exceptions while performing full scrape of all metrics",
    )

    SCRAPER_FULL_SCRAPE_TIME = Summary(
        "wargos_wled_scraper_scrape_full_scrape_time_seconds",
        "Tracks the timing for full scrape of all metrics",
    )

    WLED_SCRAPER_SCRAPE_SELF_EXCEPTIONS = Counter(
        "wargos_wled_scraper_scrape_self_exceptions_total",
        "Counts any exceptions attempting to scrape self instance",
    )

    WLED_SCRAPER_SCRAPE_SELF_TIME = Summary(
        "wargos_wled_scraper_scrape_self_time_seconds",
        "Tracks the timing for scraping self instance",
    )

    WLED_SCRAPER_SCRAPE_ALL_EXCEPTIONS = Counter(
        "wargos_wled_scraper_scrape_all_exceptions_total",
        "Counts any exceptions attempting to scrape all WLED instances",
    )

    WLED_SCRAPER_SCRAPE_ALL_TIME = Summary(
        "wargos_wled_scraper_scrape_all_time_seconds",
        "Tracks the timing for scraping all WLED instances",
    )

    WLED_SCRAPER_SCRAPE_INSTANCE_EXCEPTIONS = Counter(
        "wargos_wled_scraper_scrape_instance_exceptions_total",
        "Counts any exceptions attempting to scrape a single WLED instance",
        MetricsLabels.basic_instance_scraper_labels(),
    )

    WLED_SCRAPER_SCRAPE_INSTANCE_TIME = Summary(
        "wargos_wled_scraper_scrape_instance_time_seconds",
        "Tracks the timing for scraping a single WLED instance",
        MetricsLabels.basic_instance_scraper_labels(),
    )

    WLED_SCRAPER_SCRAPE_INSTANCE_BY_TYPE_EXCEPTIONS = Counter(
        "wargos_wled_scraper_scrape_instance_by_type_exceptions_total",
        "Counts exceptions by type while scraping a single WLED instance",
        MetricsLabels.instance_scraper_exception_labels(),
    )

    WLED_INSTANCE_SCRAPE_EVENTS_COUNTER = Counter(
        "wargos_wled_instance_scrape_events_total",
        "Count of scrape events by type per WLED instance",
        MetricsLabels.scrape_events_labels(),
    )

    WLED_INSTANCE_ONLINE = Gauge(
        "wargos_wled_instance_online",
        "Whether WLED instance is online and available (0 means offline)",
        MetricsLabels.basic_online_labels(),
    )

    INSTANCE_INFO = Gauge(
        "wargos_wled_instance_basic_info",
        "Details about the WLED instance info, mostly hw and build info",
        MetricsLabels.instance_info_labels(),
    )

    INSTANCE_FREE_HEAP = Gauge(
        "wargos_wled_instance_free_heap",
        "The current free heap of the WLED instance (in bytes)",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_UDP_PORT = Gauge(
        "wargos_wled_instance_udp_port",
        "The current udp port of the instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_UPTIME_SECONDS = Gauge(
        "wargos_wled_instance_uptime_seconds",
        "The current uptime of the instance (in seconds)",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_WEBSOCKET_CLIENTS = Gauge(
        "wargos_wled_instance_websocket_clients",
        "The number of currently connected websocket clients",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_PRESET_COUNT_VALUE = Gauge(
        "wargos_wled_instance_preset_count_value",
        "The current preset count of the instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_PRESET_IS_ON_VALUE = Gauge(
        "wargos_wled_instance_preset_is_on_value",
        "Whether the preset is on for the current wled instance",
        MetricsLabels.basic_preset_labels(),
    )

    INSTANCE_PRESET_TRANSITION_VALUE = Gauge(
        "wargos_wled_instance_preset_transition_value",
        "The crossfade transition value for the current wled instance",
        MetricsLabels.basic_preset_labels(),
    )

    INSTANCE_PRESET_QUICK_LABEL_INFO = Gauge(
        "wargos_wled_instance_preset_quick_label_info",
        "Info about the quick label for a wled instance preset",
        MetricsLabels.preset_quick_label_labels(),
    )

    INSTANCE_PALETTE_COUNT_VALUE = Gauge(
        "wargos_wled_instance_palette_count_value",
        "The current palette count of the instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_EFFECT_COUNT_VALUE = Gauge(
        "wargos_wled_instance_effect_count_value",
        "The current effect count of the instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_LED_COUNT_VALUE = Gauge(
        "wargos_wled_instance_led_count_value",
        "The current LED count of the instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_LED_FPS_VALUE = Gauge(
        "wargos_wled_instance_fps_value",
        "The current fps value of the instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_LED_MAX_POWER = Gauge(
        "wargos_wled_instance_max_power",
        "The max power value of the instance (in milliamps)",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_LED_CURRENT_POWER = Gauge(
        "wargos_wled_instance_current_power",
        "The current power value of the instance (in milliamps)",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_LED_MAX_SEGMENTS = Gauge(
        "wargos_wled_instance_max_segments",
        "The max segments value of the instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_NIGHTLIGHT_DURATION_MINUTES = Gauge(
        "wargos_wled_instance_nightlight_duration_minutes",
        "The duration of the nightlight of the instance (in minutes)",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_NIGHTLIGHT_ON_VALUE = Gauge(
        "wargos_wled_instance_nightlight_on_value",
        "The bool value of whether the nightlight of the instance is enabled",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_NIGHTLIGHT_TARGET_BRIGHTNESS_VALUE = Gauge(
        "wargos_wled_instance_nightlight_target_brightness_value",
        "The target brightness value of the nightlight of the instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_SEGMENT_COLOR_VALUE = Gauge(
        "wargos_wled_instance_segment_color_value",
        "The color value (with priority) of the segment of the instance",
        MetricsLabels.segment_color_labels(),
    )

    INSTANCE_SEGMENT_BRIGHTNESS_VALUE = Gauge(
        "wargos_wled_instance_segment_brightness_value",
        "The brightness value of the segment of the instance",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_CLONES_VALUE = Gauge(
        "wargos_wled_instance_segment_clones_value",
        "The segment this segment clones for the instance",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_EFFECT_ID_VALUE = Gauge(
        "wargos_wled_instance_segment_effect_id_value",
        "The effect_id for this instance",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_INTENSITY_VALUE = Gauge(
        "wargos_wled_instance_segment_intensity_value",
        "The intensity value for this instance",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_LENGTH_VALUE = Gauge(
        "wargos_wled_instance_segment_length_value",
        "The length for this segment",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_ON_VALUE = Gauge(
        "wargos_wled_instance_segment_on_value",
        "The bool value of whether the segment of the instance is enabled",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_PALETTE_ID_VALUE = Gauge(
        "wargos_wled_instance_segment_palette_id_value",
        "The palette_id value of the segment",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_REVERSE_VALUE = Gauge(
        "wargos_wled_instance_segment_reverse_value",
        "Flips the segment (in 2D set up) to change direction",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_SEGMENT_ID_VALUE = Gauge(
        "wargos_wled_instance_segment_id_value",
        "The segment_id value of the segment",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_SELECTED_VALUE = Gauge(
        "wargos_wled_instance_segment_selected_value",
        "The bool value of whether the segment of the instance is selected",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_SPEED_VALUE = Gauge(
        "wargos_wled_instance_segment_speed_value",
        "The relative effect speed of the segment",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_CCT_VALUE = Gauge(
        "wargos_wled_instance_segment_cct_value",
        "The white spectrum color temperature (0 is warmest, 255 is coldest)",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_START_VALUE = Gauge(
        "wargos_wled_instance_segment_start_value",
        "For 2-D set up, this determines segment starts (from top left)",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_SEGMENT_STOP_VALUE = Gauge(
        "wargos_wled_instance_segment_stop_value",
        "For 2D set up, this determines segment starts (from top left)",
        MetricsLabels.basic_segment_labels(),
    )

    INSTANCE_FILESYSTEM_SPACE_TOTAL = Gauge(
        "wargos_wled_instance_filesystem_space_kb_total",
        "The total space of the filesystem (in kb)",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_FILESYSTEM_SPACE_USED = Gauge(
        "wargos_wled_instance_filesystem_space_kb_used",
        "The used space of the filesystem (in kb)",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_WIFI_CHANNEL = Gauge(
        "wargos_wled_instance_wifi_channel",
        "The current wifi channel of the WLED instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_WIFI_RSSI = Gauge(
        "wargos_wled_instance_wifi_rssi",
        "The current wifi RSSI of the WLED instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_WIFI_SIGNAL = Gauge(
        "wargos_wled_instance_wifi_signal",
        "The current wifi signal of the WLED instance",
        MetricsLabels.basic_info_labels(),
    )

    INSTANCE_WIFI_BSSID = Gauge(
        "wargos_wled_instance_wifi_bssid",
        "The current bssid of the wifi the WLED instance is connected to",
        MetricsLabels.wifi_bssid_labels(),
    )

    INSTANCE_LIVE_STATE = Gauge(
        "wargos_wled_instance_live_state",
        "The current WLED instance live state bool value",
        MetricsLabels.basic_state_labels(),
    )

    INSTANCE_STATE_BRIGHTNESS = Gauge(
        "wargos_wled_instance_state_brightness",
        "The current WLED instance brightness",
        MetricsLabels.basic_state_labels(),
    )

    INSTANCE_STATE_TRANSITION = Gauge(
        "wargos_wled_instance_state_transition",
        "Duration of crossfade between colors/brightness (1 unit is 100ms)",
        MetricsLabels.basic_state_labels(),
    )

    INSTANCE_STATE_ON = Gauge(
        "wargos_wled_instance_state_on",
        "The current WLED instance is on value",
        MetricsLabels.basic_state_labels(),
    )

    INSTANCE_STATE_PLAYLIST_ID = Gauge(
        "wargos_wled_instance_state_playlist_id",
        "The current WLED instance playlist_id",
        MetricsLabels.basic_state_labels(),
    )

    INSTANCE_STATE_PRESET_ID = Gauge(
        "wargos_wled_instance_state_preset_id",
        "The current WLED instance preset_id",
        MetricsLabels.basic_state_labels(),
    )

    INSTANCE_SYNC_RECEIVE_STATE = Gauge(
        "wargos_wled_instance_sync_receive_state",
        "The current state of the WLED instance sync receive setting",
        MetricsLabels.basic_udp_sync_labels(),
    )

    INSTANCE_SYNC_SEND_STATE = Gauge(
        "wargos_wled_instance_sync_send_state",
        "The current state of the WLED instance sync send setting",
        MetricsLabels.basic_udp_sync_labels(),
    )

    INSTANCE_SYNC_RECEIVE_GROUPS = Gauge(
        "wargos_wled_instance_sync_receive_groups",
        "The current state of the WLED instance sync receive groups",
        MetricsLabels.basic_udp_sync_labels(),
    )

    INSTANCE_SYNC_SEND_GROUPS = Gauge(
        "wargos_wled_instance_sync_send_groups",
        "The current state of the WLED instance sync send groups",
        MetricsLabels.basic_udp_sync_labels(),
    )

    # Backup Metrics (consolidated for both config and preset operations)
    BACKUP_OPERATIONS_TOTAL = Counter(
        "wargos_backup_operations_total",
        "Total number of backup operations",
        MetricsLabels.backup_operations_labels(),
    )

    BACKUP_OPERATION_DURATION = Summary(
        "wargos_backup_operation_duration_seconds",
        "Duration of backup operations",
        MetricsLabels.backup_operation_duration_labels(),
    )

    BACKUP_OPERATION_EXCEPTIONS = Counter(
        "wargos_backup_operation_exceptions_total",
        "Total number of exceptions during backup operations",
        MetricsLabels.backup_operation_exceptions_labels(),
    )

    BACKUP_FILES_CREATED = Counter(
        "wargos_backup_files_created_total",
        "Total number of backup files created",
        MetricsLabels.backup_files_created_labels(),
    )

    BACKUP_FILE_SIZE_BYTES = Gauge(
        "wargos_backup_file_size_bytes",
        "Size of the most recent backup file in bytes",
        MetricsLabels.backup_file_size_labels(),
    )

    BACKUP_HTTP_ERRORS = Counter(
        "wargos_backup_http_errors_total",
        "Total number of HTTP errors during backup operations",
        MetricsLabels.backup_http_errors_labels(),
    )

    BACKUP_CONNECTION_ERRORS = Counter(
        "wargos_backup_connection_errors_total",
        "Total number of connection errors during backup operations",
        MetricsLabels.backup_connection_errors_labels(),
    )

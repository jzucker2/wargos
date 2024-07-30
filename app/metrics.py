from prometheus_client import Gauge, Counter, Summary


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
    def basic_info_labels(cls):
        return list([
            cls.NAME,
            cls.IP,
        ])

    @classmethod
    def basic_client_labels(cls):
        return list([
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
    WLED_CLIENT_SIMPLE_TEST_COUNTER = Counter(
        'wargos_wled_client_simple_test_total',
        'Count of times the simple WLED client test is run',
        MetricsLabels.basic_client_labels()
    )

    WLED_CLIENT_CONNECT_EXCEPTIONS = Counter(
        'wargos_wled_client_connect_exceptions_total',
        'Counts any exceptions attempting to connect to a WLED instance',
        MetricsLabels.basic_client_labels()
    )

    WLED_CLIENT_CONNECT_TIME = Summary(
        'wargos_wled_client_connect_time_seconds',
        'Tracks the timing for a wled instance connection',
        MetricsLabels.basic_client_labels()
    )

    INSTANCE_INFO = Gauge(
        'wargos_wled_instance_basic_info',
        'Details about the WLED instance info, mostly hw and build info',
        MetricsLabels.instance_info_labels()
    )

    INSTANCE_FREE_HEAP = Gauge(
        'wargos_wled_instance_free_heap',
        'The current free heap of the WLED instance (in MB?)',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_UDP_PORT = Gauge(
        'wargos_wled_instance_udp_port',
        'The current udp port of the instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_UPTIME_SECONDS = Gauge(
        'wargos_wled_instance_uptime_seconds',
        'The current uptime of the instance (in seconds)',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_PALETTE_COUNT_VALUE = Gauge(
        'wargos_wled_instance_palette_count_value',
        'The current palette count of the instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_EFFECT_COUNT_VALUE = Gauge(
        'wargos_wled_instance_effect_count_value',
        'The current effect count of the instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_LED_COUNT_VALUE = Gauge(
        'wargos_wled_instance_led_count_value',
        'The current LED count of the instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_LED_FPS_VALUE = Gauge(
        'wargos_wled_instance_fps_value',
        'The current fps value of the instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_LED_MAX_POWER = Gauge(
        'wargos_wled_instance_max_power',
        'The max power value of the instance (in milliamps)',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_LED_CURRENT_POWER = Gauge(
        'wargos_wled_instance_current_power',
        'The current power value of the instance (in milliamps)',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_LED_MAX_SEGMENTS = Gauge(
        'wargos_wled_instance_max_segments',
        'The max segments value of the instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_NIGHTLIGHT_DURATION_MINUTES = Gauge(
        'wargos_wled_instance_nightlight_duration_minutes',
        'The duration of the nightlight of the instance (in minutes)',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_NIGHTLIGHT_ON_VALUE = Gauge(
        'wargos_wled_instance_nightlight_on_value',
        'The bool value of whether the nightlight of the instance is enabled',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_NIGHTLIGHT_TARGET_BRIGHTNESS_VALUE = Gauge(
        'wargos_wled_instance_nightlight_target_brightness_value',
        'The target brightness value of the nightlight of the instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_WIFI_CHANNEL = Gauge(
        'wargos_wled_instance_wifi_channel',
        'The current wifi channel of the WLED instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_WIFI_RSSI = Gauge(
        'wargos_wled_instance_wifi_rssi',
        'The current wifi RSSI of the WLED instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_WIFI_SIGNAL = Gauge(
        'wargos_wled_instance_wifi_signal',
        'The current wifi signal of the WLED instance',
        MetricsLabels.basic_info_labels()
    )

    INSTANCE_LIVE_STATE = Gauge(
        'wargos_wled_instance_live_state',
        'The current WLED instance live state bool value',
        MetricsLabels.basic_state_labels()
    )

    INSTANCE_STATE_BRIGHTNESS = Gauge(
        'wargos_wled_instance_state_brightness',
        'The current WLED instance brightness',
        MetricsLabels.basic_state_labels()
    )

    INSTANCE_STATE_ON = Gauge(
        'wargos_wled_instance_state_on',
        'The current WLED instance is on value',
        MetricsLabels.basic_state_labels()
    )

    INSTANCE_STATE_PLAYLIST_ID = Gauge(
        'wargos_wled_instance_state_playlist_id',
        'The current WLED instance playlist_id',
        MetricsLabels.basic_state_labels()
    )

    INSTANCE_STATE_PRESET_ID = Gauge(
        'wargos_wled_instance_state_preset_id',
        'The current WLED instance preset_id',
        MetricsLabels.basic_state_labels()
    )

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

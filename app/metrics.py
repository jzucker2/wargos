from prometheus_client import Gauge


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
        MetricsLabels.basic_info_labels())

    INSTANCE_WIFI_CHANNEL = Gauge(
        'wargos_wled_instance_wifi_channel',
        'The current wifi channel of the WLED instance',
        MetricsLabels.basic_info_labels())

    INSTANCE_WIFI_RSSI = Gauge(
        'wargos_wled_instance_wifi_rssi',
        'The current wifi RSSI of the WLED instance',
        MetricsLabels.basic_info_labels())

    INSTANCE_WIFI_SIGNAL = Gauge(
        'wargos_wled_instance_wifi_signal',
        'The current wifi signal of the WLED instance',
        MetricsLabels.basic_info_labels())

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

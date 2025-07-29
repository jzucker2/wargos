import unittest

from app.metrics import Metrics, MetricsLabels


class TestMetricsLabelsDetailed(unittest.TestCase):
    """Comprehensive tests for MetricsLabels enum"""

    def test_all_label_values(self):
        """Test that all label values are strings"""
        for label in MetricsLabels:
            self.assertIsInstance(label.value, str)
            self.assertGreater(len(label.value), 0)

    def test_releases_labels(self):
        """Test releases_labels method returns correct labels"""
        labels = MetricsLabels.releases_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 3)
        self.assertIn("stable", labels)
        self.assertIn("beta", labels)
        self.assertIn("pid", labels)

    def test_wargos_instance_info_labels(self):
        """Test wargos_instance_info_labels method"""
        labels = MetricsLabels.wargos_instance_info_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("version", labels)
        self.assertIn("pid", labels)

    def test_instance_info_labels(self):
        """Test instance_info_labels method"""
        labels = MetricsLabels.instance_info_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 9)
        expected_labels = [
            "architecture",
            "arduino_core_version",
            "brand",
            "build",
            "ip",
            "mac_address",
            "name",
            "product",
            "version",
        ]
        for label in expected_labels:
            self.assertIn(label, labels)

    def test_basic_info_labels(self):
        """Test basic_info_labels method"""
        labels = MetricsLabels.basic_info_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 3)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)
        self.assertIn("pid", labels)

    def test_scrape_events_labels(self):
        """Test scrape_events_labels method"""
        labels = MetricsLabels.scrape_events_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 3)
        self.assertIn("ip", labels)
        self.assertIn("scrape_event", labels)
        self.assertIn("pid", labels)

    def test_wifi_bssid_labels(self):
        """Test wifi_bssid_labels method"""
        labels = MetricsLabels.wifi_bssid_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 4)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)
        self.assertIn("bssid", labels)
        self.assertIn("pid", labels)

    def test_basic_segment_labels(self):
        """Test basic_segment_labels method"""
        labels = MetricsLabels.basic_segment_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 4)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)
        self.assertIn("segment", labels)
        self.assertIn("pid", labels)

    def test_segment_color_labels(self):
        """Test segment_color_labels method"""
        labels = MetricsLabels.segment_color_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 5)
        expected_labels = [
            "name",
            "ip",
            "segment",
            "color_priority",
            "color_tuple_position",
        ]
        for label in expected_labels:
            self.assertIn(label, labels)

    def test_basic_client_labels(self):
        """Test basic_client_labels method"""
        labels = MetricsLabels.basic_client_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("ip", labels)
        self.assertIn("pid", labels)

    def test_basic_online_labels(self):
        """Test basic_online_labels method"""
        labels = MetricsLabels.basic_online_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("ip", labels)
        self.assertIn("pid", labels)

    def test_basic_instance_scraper_labels(self):
        """Test basic_instance_scraper_labels method"""
        labels = MetricsLabels.basic_instance_scraper_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("ip", labels)
        self.assertIn("pid", labels)

    def test_instance_scraper_exception_labels(self):
        """Test instance_scraper_exception_labels method"""
        labels = MetricsLabels.instance_scraper_exception_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 3)
        self.assertIn("ip", labels)
        self.assertIn("exception_class", labels)
        self.assertIn("pid", labels)

    def test_basic_state_labels(self):
        """Test basic_state_labels method"""
        labels = MetricsLabels.basic_state_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 3)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)
        self.assertIn("pid", labels)

    def test_basic_udp_sync_labels(self):
        """Test basic_udp_sync_labels method"""
        labels = MetricsLabels.basic_udp_sync_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 3)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)
        self.assertIn("pid", labels)

    def test_basic_preset_labels(self):
        """Test basic_preset_labels method"""
        labels = MetricsLabels.basic_preset_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 5)
        expected_labels = ["name", "ip", "preset_id", "preset_name", "pid"]
        for label in expected_labels:
            self.assertIn(label, labels)

    def test_preset_quick_label_labels(self):
        """Test preset_quick_label_labels method"""
        labels = MetricsLabels.preset_quick_label_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 6)
        expected_labels = [
            "name",
            "ip",
            "preset_id",
            "preset_name",
            "preset_quick_label",
            "pid",
        ]
        for label in expected_labels:
            self.assertIn(label, labels)


class TestMetricsDetailed(unittest.TestCase):
    """Comprehensive tests for Metrics class"""

    def test_wargos_instance_info_metric(self):
        """Test WARGOS_INSTANCE_INFO metric configuration"""
        metric = Metrics.WARGOS_INSTANCE_INFO
        self.assertEqual(metric._name, "wargos_instance_info")
        self.assertEqual(
            metric._documentation,
            "Details about the actual wargos scraper instance (this app)",
        )
        self.assertEqual(metric._labelnames, ("version", "pid"))

    def test_wled_client_metrics(self):
        """Test WLED client related metrics"""
        # Simple test counter
        metric = Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER
        self.assertEqual(metric._name, "wargos_wled_client_simple_test")
        self.assertEqual(metric._labelnames, ("ip", "pid"))

        # Connect exceptions
        metric = Metrics.WLED_CLIENT_CONNECT_EXCEPTIONS
        self.assertEqual(metric._name, "wargos_wled_client_connect_exceptions")
        self.assertEqual(metric._labelnames, ("ip", "pid"))

        # Connect time
        metric = Metrics.WLED_CLIENT_CONNECT_TIME
        self.assertEqual(
            metric._name, "wargos_wled_client_connect_time_seconds"
        )
        self.assertEqual(metric._labelnames, ("ip", "pid"))

    def test_wled_releases_metrics(self):
        """Test WLED releases related metrics"""
        # Connect exceptions
        metric = Metrics.WLED_RELEASES_CONNECT_EXCEPTIONS
        self.assertEqual(
            metric._name, "wargos_wled_releases_connect_exceptions"
        )
        self.assertEqual(metric._labelnames, ())

        # Connect time
        metric = Metrics.WLED_RELEASES_CONNECT_TIME
        self.assertEqual(
            metric._name, "wargos_wled_releases_connect_time_seconds"
        )
        self.assertEqual(metric._labelnames, ())

        # Releases info
        metric = Metrics.WLED_RELEASES_INFO
        self.assertEqual(metric._name, "wargos_wled_releases_basic_info")
        self.assertEqual(metric._labelnames, ("stable", "beta", "pid"))

    def test_scraper_metrics(self):
        """Test scraper related metrics"""
        # Scrape releases exceptions
        metric = Metrics.SCRAPER_SCRAPE_RELEASES_EXCEPTIONS
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_releases_exceptions"
        )
        self.assertEqual(metric._labelnames, ())

        # Scrape releases time
        metric = Metrics.SCRAPER_SCRAPE_RELEASES_TIME
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_releases_time_seconds"
        )
        self.assertEqual(metric._labelnames, ())

        # Full scrape exceptions
        metric = Metrics.SCRAPER_FULL_SCRAPE_EXCEPTIONS
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_full_scrape_exceptions"
        )
        self.assertEqual(metric._labelnames, ())

        # Full scrape time
        metric = Metrics.SCRAPER_FULL_SCRAPE_TIME
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_full_scrape_time_seconds"
        )
        self.assertEqual(metric._labelnames, ())

    def test_wled_scraper_metrics(self):
        """Test WLED scraper related metrics"""
        # Scrape self exceptions
        metric = Metrics.WLED_SCRAPER_SCRAPE_SELF_EXCEPTIONS
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_self_exceptions"
        )
        self.assertEqual(metric._labelnames, ())

        # Scrape self time
        metric = Metrics.WLED_SCRAPER_SCRAPE_SELF_TIME
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_self_time_seconds"
        )
        self.assertEqual(metric._labelnames, ())

        # Scrape all exceptions
        metric = Metrics.WLED_SCRAPER_SCRAPE_ALL_EXCEPTIONS
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_all_exceptions"
        )
        self.assertEqual(metric._labelnames, ())

        # Scrape all time
        metric = Metrics.WLED_SCRAPER_SCRAPE_ALL_TIME
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_all_time_seconds"
        )
        self.assertEqual(metric._labelnames, ())

        # Scrape instance exceptions
        metric = Metrics.WLED_SCRAPER_SCRAPE_INSTANCE_EXCEPTIONS
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_instance_exceptions"
        )
        self.assertEqual(metric._labelnames, ("ip", "pid"))

        # Scrape instance time
        metric = Metrics.WLED_SCRAPER_SCRAPE_INSTANCE_TIME
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_instance_time_seconds"
        )
        self.assertEqual(metric._labelnames, ("ip", "pid"))

    def test_instance_metrics(self):
        """Test instance related metrics"""
        # Instance online
        metric = Metrics.WLED_INSTANCE_ONLINE
        self.assertEqual(metric._name, "wargos_wled_instance_online")
        self.assertEqual(metric._labelnames, ("ip", "pid"))

        # Instance info
        metric = Metrics.INSTANCE_INFO
        self.assertEqual(metric._name, "wargos_wled_instance_basic_info")
        self.assertEqual(
            metric._labelnames,
            (
                "architecture",
                "arduino_core_version",
                "brand",
                "build",
                "ip",
                "mac_address",
                "name",
                "product",
                "version",
            ),
        )

        # Instance free heap
        metric = Metrics.INSTANCE_FREE_HEAP
        self.assertEqual(metric._name, "wargos_wled_instance_free_heap")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Instance UDP port
        metric = Metrics.INSTANCE_UDP_PORT
        self.assertEqual(metric._name, "wargos_wled_instance_udp_port")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Instance uptime
        metric = Metrics.INSTANCE_UPTIME_SECONDS
        self.assertEqual(metric._name, "wargos_wled_instance_uptime_seconds")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Instance websocket clients
        metric = Metrics.INSTANCE_WEBSOCKET_CLIENTS
        self.assertEqual(
            metric._name, "wargos_wled_instance_websocket_clients"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

    def test_preset_metrics(self):
        """Test preset related metrics"""
        # Preset count
        metric = Metrics.INSTANCE_PRESET_COUNT_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_preset_count_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Preset is on
        metric = Metrics.INSTANCE_PRESET_IS_ON_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_preset_is_on_value"
        )
        self.assertEqual(
            metric._labelnames,
            ("name", "ip", "preset_id", "preset_name", "pid"),
        )

        # Preset transition
        metric = Metrics.INSTANCE_PRESET_TRANSITION_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_preset_transition_value"
        )
        self.assertEqual(
            metric._labelnames,
            ("name", "ip", "preset_id", "preset_name", "pid"),
        )

        # Preset quick label info
        metric = Metrics.INSTANCE_PRESET_QUICK_LABEL_INFO
        self.assertEqual(
            metric._name, "wargos_wled_instance_preset_quick_label_info"
        )
        self.assertEqual(
            metric._labelnames,
            (
                "name",
                "ip",
                "preset_id",
                "preset_name",
                "preset_quick_label",
                "pid",
            ),
        )

    def test_led_metrics(self):
        """Test LED related metrics"""
        # Palette count
        metric = Metrics.INSTANCE_PALETTE_COUNT_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_palette_count_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Effect count
        metric = Metrics.INSTANCE_EFFECT_COUNT_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_effect_count_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # LED count
        metric = Metrics.INSTANCE_LED_COUNT_VALUE
        self.assertEqual(metric._name, "wargos_wled_instance_led_count_value")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # LED FPS
        metric = Metrics.INSTANCE_LED_FPS_VALUE
        self.assertEqual(metric._name, "wargos_wled_instance_fps_value")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # LED max power
        metric = Metrics.INSTANCE_LED_MAX_POWER
        self.assertEqual(metric._name, "wargos_wled_instance_max_power")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # LED current power
        metric = Metrics.INSTANCE_LED_CURRENT_POWER
        self.assertEqual(metric._name, "wargos_wled_instance_current_power")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # LED max segments
        metric = Metrics.INSTANCE_LED_MAX_SEGMENTS
        self.assertEqual(metric._name, "wargos_wled_instance_max_segments")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

    def test_nightlight_metrics(self):
        """Test nightlight related metrics"""
        # Nightlight duration
        metric = Metrics.INSTANCE_NIGHTLIGHT_DURATION_MINUTES
        self.assertEqual(
            metric._name, "wargos_wled_instance_nightlight_duration_minutes"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Nightlight on
        metric = Metrics.INSTANCE_NIGHTLIGHT_ON_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_nightlight_on_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Nightlight target brightness
        metric = Metrics.INSTANCE_NIGHTLIGHT_TARGET_BRIGHTNESS_VALUE
        self.assertEqual(
            metric._name,
            "wargos_wled_instance_nightlight_target_brightness_value",
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

    def test_segment_metrics(self):
        """Test segment related metrics"""
        # Segment color
        metric = Metrics.INSTANCE_SEGMENT_COLOR_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_color_value"
        )
        self.assertEqual(
            metric._labelnames,
            (
                "name",
                "ip",
                "segment",
                "color_priority",
                "color_tuple_position",
            ),
        )

        # Segment brightness
        metric = Metrics.INSTANCE_SEGMENT_BRIGHTNESS_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_brightness_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment clones
        metric = Metrics.INSTANCE_SEGMENT_CLONES_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_clones_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment effect ID
        metric = Metrics.INSTANCE_SEGMENT_EFFECT_ID_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_effect_id_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment intensity
        metric = Metrics.INSTANCE_SEGMENT_INTENSITY_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_intensity_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment length
        metric = Metrics.INSTANCE_SEGMENT_LENGTH_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_length_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment on
        metric = Metrics.INSTANCE_SEGMENT_ON_VALUE
        self.assertEqual(metric._name, "wargos_wled_instance_segment_on_value")
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment palette ID
        metric = Metrics.INSTANCE_SEGMENT_PALETTE_ID_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_palette_id_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment reverse
        metric = Metrics.INSTANCE_SEGMENT_REVERSE_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_reverse_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment segment ID
        metric = Metrics.INSTANCE_SEGMENT_SEGMENT_ID_VALUE
        self.assertEqual(metric._name, "wargos_wled_instance_segment_id_value")
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment selected
        metric = Metrics.INSTANCE_SEGMENT_SELECTED_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_selected_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment speed
        metric = Metrics.INSTANCE_SEGMENT_SPEED_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_speed_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment CCT
        metric = Metrics.INSTANCE_SEGMENT_CCT_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_cct_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment start
        metric = Metrics.INSTANCE_SEGMENT_START_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_start_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

        # Segment stop
        metric = Metrics.INSTANCE_SEGMENT_STOP_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_segment_stop_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "segment", "pid"))

    def test_filesystem_metrics(self):
        """Test filesystem related metrics"""
        # Filesystem space total
        metric = Metrics.INSTANCE_FILESYSTEM_SPACE_TOTAL
        self.assertEqual(
            metric._name, "wargos_wled_instance_filesystem_space_kb_total"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Filesystem space used
        metric = Metrics.INSTANCE_FILESYSTEM_SPACE_USED
        self.assertEqual(
            metric._name, "wargos_wled_instance_filesystem_space_kb_used"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

    def test_wifi_metrics(self):
        """Test WiFi related metrics"""
        # WiFi channel
        metric = Metrics.INSTANCE_WIFI_CHANNEL
        self.assertEqual(metric._name, "wargos_wled_instance_wifi_channel")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # WiFi RSSI
        metric = Metrics.INSTANCE_WIFI_RSSI
        self.assertEqual(metric._name, "wargos_wled_instance_wifi_rssi")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # WiFi signal
        metric = Metrics.INSTANCE_WIFI_SIGNAL
        self.assertEqual(metric._name, "wargos_wled_instance_wifi_signal")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # WiFi BSSID
        metric = Metrics.INSTANCE_WIFI_BSSID
        self.assertEqual(metric._name, "wargos_wled_instance_wifi_bssid")
        self.assertEqual(metric._labelnames, ("name", "ip", "bssid", "pid"))

    def test_state_metrics(self):
        """Test state related metrics"""
        # Live state
        metric = Metrics.INSTANCE_LIVE_STATE
        self.assertEqual(metric._name, "wargos_wled_instance_live_state")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # State brightness
        metric = Metrics.INSTANCE_STATE_BRIGHTNESS
        self.assertEqual(metric._name, "wargos_wled_instance_state_brightness")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # State transition
        metric = Metrics.INSTANCE_STATE_TRANSITION
        self.assertEqual(metric._name, "wargos_wled_instance_state_transition")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # State on
        metric = Metrics.INSTANCE_STATE_ON
        self.assertEqual(metric._name, "wargos_wled_instance_state_on")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # State playlist ID
        metric = Metrics.INSTANCE_STATE_PLAYLIST_ID
        self.assertEqual(
            metric._name, "wargos_wled_instance_state_playlist_id"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # State preset ID
        metric = Metrics.INSTANCE_STATE_PRESET_ID
        self.assertEqual(metric._name, "wargos_wled_instance_state_preset_id")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

    def test_sync_metrics(self):
        """Test sync related metrics"""
        # Sync receive state
        metric = Metrics.INSTANCE_SYNC_RECEIVE_STATE
        self.assertEqual(
            metric._name, "wargos_wled_instance_sync_receive_state"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Sync send state
        metric = Metrics.INSTANCE_SYNC_SEND_STATE
        self.assertEqual(metric._name, "wargos_wled_instance_sync_send_state")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Sync receive groups
        metric = Metrics.INSTANCE_SYNC_RECEIVE_GROUPS
        self.assertEqual(
            metric._name, "wargos_wled_instance_sync_receive_groups"
        )
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

        # Sync send groups
        metric = Metrics.INSTANCE_SYNC_SEND_GROUPS
        self.assertEqual(metric._name, "wargos_wled_instance_sync_send_groups")
        self.assertEqual(metric._labelnames, ("name", "ip", "pid"))

    def test_metric_types(self):
        """Test that metrics have correct types"""
        # Test Gauge metrics
        self.assertIsInstance(
            Metrics.WARGOS_INSTANCE_INFO, type(Metrics.WARGOS_INSTANCE_INFO)
        )
        self.assertIsInstance(
            Metrics.WLED_INSTANCE_ONLINE, type(Metrics.WLED_INSTANCE_ONLINE)
        )
        self.assertIsInstance(
            Metrics.INSTANCE_INFO, type(Metrics.INSTANCE_INFO)
        )

        # Test Counter metrics
        self.assertIsInstance(
            Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER,
            type(Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER),
        )
        self.assertIsInstance(
            Metrics.WLED_CLIENT_CONNECT_EXCEPTIONS,
            type(Metrics.WLED_CLIENT_CONNECT_EXCEPTIONS),
        )

        # Test Summary metrics
        self.assertIsInstance(
            Metrics.WLED_CLIENT_CONNECT_TIME,
            type(Metrics.WLED_CLIENT_CONNECT_TIME),
        )
        self.assertIsInstance(
            Metrics.WLED_RELEASES_CONNECT_TIME,
            type(Metrics.WLED_RELEASES_CONNECT_TIME),
        )

    def test_metric_documentation(self):
        """Test that metrics have documentation"""
        # Test a few key metrics have documentation
        self.assertIsInstance(Metrics.WARGOS_INSTANCE_INFO._documentation, str)
        self.assertGreater(len(Metrics.WARGOS_INSTANCE_INFO._documentation), 0)

        self.assertIsInstance(
            Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER._documentation, str
        )
        self.assertGreater(
            len(Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER._documentation), 0
        )

        self.assertIsInstance(Metrics.INSTANCE_INFO._documentation, str)
        self.assertGreater(len(Metrics.INSTANCE_INFO._documentation), 0)


if __name__ == "__main__":
    unittest.main()

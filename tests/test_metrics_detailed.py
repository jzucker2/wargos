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
        """Test releases labels"""
        labels = MetricsLabels.releases_labels()
        assert len(labels) == 2
        assert "stable" in labels
        assert "beta" in labels

    def test_wargos_instance_info_labels(self):
        """Test wargos instance info labels"""
        labels = MetricsLabels.wargos_instance_info_labels()
        assert len(labels) == 1
        assert "version" in labels

    def test_instance_info_labels(self):
        """Test instance info labels"""
        labels = MetricsLabels.instance_info_labels()
        assert len(labels) == 9
        assert "architecture" in labels
        assert "arduino_core_version" in labels
        assert "brand" in labels
        assert "build" in labels
        assert "ip" in labels
        assert "mac_address" in labels
        assert "name" in labels
        assert "product" in labels
        assert "version" in labels

    def test_basic_info_labels(self):
        """Test basic_info_labels method"""
        labels = MetricsLabels.basic_info_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)

    def test_scrape_events_labels(self):
        """Test scrape_events_labels method"""
        labels = MetricsLabels.scrape_events_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("ip", labels)
        self.assertIn("scrape_event", labels)

    def test_wifi_bssid_labels(self):
        """Test wifi_bssid_labels method"""
        labels = MetricsLabels.wifi_bssid_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 3)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)
        self.assertIn("bssid", labels)

    def test_basic_segment_labels(self):
        """Test basic_segment_labels method"""
        labels = MetricsLabels.basic_segment_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 3)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)
        self.assertIn("segment", labels)

    def test_segment_color_labels(self):
        """Test segment color labels"""
        labels = MetricsLabels.segment_color_labels()
        assert len(labels) == 5
        assert "name" in labels
        assert "ip" in labels
        assert "segment" in labels
        assert "color_priority" in labels
        assert "color_tuple_position" in labels

    def test_basic_client_labels(self):
        """Test basic_client_labels method"""
        labels = MetricsLabels.basic_client_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 1)
        self.assertIn("ip", labels)

    def test_basic_online_labels(self):
        """Test basic_online_labels method"""
        labels = MetricsLabels.basic_online_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 1)
        self.assertIn("ip", labels)

    def test_basic_instance_scraper_labels(self):
        """Test basic_instance_scraper_labels method"""
        labels = MetricsLabels.basic_instance_scraper_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 1)
        self.assertIn("ip", labels)

    def test_instance_scraper_exception_labels(self):
        """Test instance_scraper_exception_labels method"""
        labels = MetricsLabels.instance_scraper_exception_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("ip", labels)
        self.assertIn("exception_class", labels)

    def test_basic_state_labels(self):
        """Test basic_state_labels method"""
        labels = MetricsLabels.basic_state_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)

    def test_basic_udp_sync_labels(self):
        """Test basic_udp_sync_labels method"""
        labels = MetricsLabels.basic_udp_sync_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 2)
        self.assertIn("name", labels)
        self.assertIn("ip", labels)

    def test_basic_preset_labels(self):
        """Test basic_preset_labels method"""
        labels = MetricsLabels.basic_preset_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 4)
        expected_labels = ["name", "ip", "preset_id", "preset_name"]
        for label in expected_labels:
            self.assertIn(label, labels)

    def test_preset_quick_label_labels(self):
        """Test preset_quick_label_labels method"""
        labels = MetricsLabels.preset_quick_label_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(len(labels), 5)
        expected_labels = [
            "name",
            "ip",
            "preset_id",
            "preset_name",
            "preset_quick_label",
        ]
        for label in expected_labels:
            self.assertIn(label, labels)


class TestMetricsDetailed(unittest.TestCase):
    """Comprehensive tests for Metrics class"""

    def test_wargos_instance_info_metric(self):
        """Test WARGOS_INSTANCE_INFO metric"""
        metric = Metrics.WARGOS_INSTANCE_INFO
        self.assertEqual(metric._name, "wargos_instance_info")
        self.assertEqual(metric._type, "gauge")
        self.assertEqual(metric._labelnames, ("version",))

    def test_wled_client_metrics(self):
        """Test WLED client related metrics"""
        # Simple test counter
        metric = Metrics.WLED_CLIENT_SIMPLE_TEST_COUNTER
        self.assertEqual(metric._name, "wargos_wled_client_simple_test")
        self.assertEqual(metric._labelnames, ("ip",))

        # Connect exceptions
        metric = Metrics.WLED_CLIENT_CONNECT_EXCEPTIONS
        self.assertEqual(metric._name, "wargos_wled_client_connect_exceptions")
        self.assertEqual(metric._labelnames, ("ip",))

        # Connect time
        metric = Metrics.WLED_CLIENT_CONNECT_TIME
        self.assertEqual(
            metric._name, "wargos_wled_client_connect_time_seconds"
        )
        self.assertEqual(metric._labelnames, ("ip",))

    def test_wled_releases_metrics(self):
        """Test WLED_RELEASES_INFO metric"""
        metric = Metrics.WLED_RELEASES_INFO
        self.assertEqual(metric._name, "wargos_wled_releases_basic_info")
        self.assertEqual(metric._type, "gauge")
        self.assertEqual(metric._labelnames, ("stable", "beta"))

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
        self.assertEqual(metric._labelnames, ("ip",))

        # Scrape instance time
        metric = Metrics.WLED_SCRAPER_SCRAPE_INSTANCE_TIME
        self.assertEqual(
            metric._name, "wargos_wled_scraper_scrape_instance_time_seconds"
        )
        self.assertEqual(metric._labelnames, ("ip",))

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

    def test_instance_metrics(self):
        """Test instance related metrics"""
        # Instance online
        metric = Metrics.WLED_INSTANCE_ONLINE
        self.assertEqual(metric._name, "wargos_wled_instance_online")
        self.assertEqual(metric._labelnames, ("ip",))

        # Instance info
        metric = Metrics.INSTANCE_INFO
        self.assertEqual(metric._name, "wargos_wled_instance_basic_info")
        self.assertEqual(metric._type, "gauge")
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
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Instance UDP port
        metric = Metrics.INSTANCE_UDP_PORT
        self.assertEqual(metric._name, "wargos_wled_instance_udp_port")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Instance uptime
        metric = Metrics.INSTANCE_UPTIME_SECONDS
        self.assertEqual(metric._name, "wargos_wled_instance_uptime_seconds")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Instance websocket clients
        metric = Metrics.INSTANCE_WEBSOCKET_CLIENTS
        self.assertEqual(
            metric._name, "wargos_wled_instance_websocket_clients"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

    def test_preset_metrics(self):
        """Test preset related metrics"""
        # Preset count
        metric = Metrics.INSTANCE_PRESET_COUNT_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_preset_count_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Preset is on
        metric = Metrics.INSTANCE_PRESET_IS_ON_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_preset_is_on_value"
        )
        self.assertEqual(
            metric._labelnames,
            ("name", "ip", "preset_id", "preset_name"),
        )

        # Preset transition
        metric = Metrics.INSTANCE_PRESET_TRANSITION_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_preset_transition_value"
        )
        self.assertEqual(
            metric._labelnames,
            ("name", "ip", "preset_id", "preset_name"),
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
            ),
        )

    def test_led_metrics(self):
        """Test LED related metrics"""
        # LED count
        metric = Metrics.INSTANCE_LED_COUNT_VALUE
        self.assertEqual(metric._name, "wargos_wled_instance_led_count_value")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # LED FPS
        metric = Metrics.INSTANCE_LED_FPS_VALUE
        self.assertEqual(metric._name, "wargos_wled_instance_fps_value")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # LED max power
        metric = Metrics.INSTANCE_LED_MAX_POWER
        self.assertEqual(metric._name, "wargos_wled_instance_max_power")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # LED current power
        metric = Metrics.INSTANCE_LED_CURRENT_POWER
        self.assertEqual(metric._name, "wargos_wled_instance_current_power")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # LED max segments
        metric = Metrics.INSTANCE_LED_MAX_SEGMENTS
        self.assertEqual(metric._name, "wargos_wled_instance_max_segments")
        self.assertEqual(metric._labelnames, ("name", "ip"))

    def test_nightlight_metrics(self):
        """Test nightlight related metrics"""
        # Nightlight duration
        metric = Metrics.INSTANCE_NIGHTLIGHT_DURATION_MINUTES
        self.assertEqual(
            metric._name, "wargos_wled_instance_nightlight_duration_minutes"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Nightlight on
        metric = Metrics.INSTANCE_NIGHTLIGHT_ON_VALUE
        self.assertEqual(
            metric._name, "wargos_wled_instance_nightlight_on_value"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Nightlight target brightness
        metric = Metrics.INSTANCE_NIGHTLIGHT_TARGET_BRIGHTNESS_VALUE
        self.assertEqual(
            metric._name,
            "wargos_wled_instance_nightlight_target_brightness_value",
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

    def test_filesystem_metrics(self):
        """Test filesystem related metrics"""
        # Filesystem space total
        metric = Metrics.INSTANCE_FILESYSTEM_SPACE_TOTAL
        self.assertEqual(
            metric._name, "wargos_wled_instance_filesystem_space_kb_total"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Filesystem space used
        metric = Metrics.INSTANCE_FILESYSTEM_SPACE_USED
        self.assertEqual(
            metric._name, "wargos_wled_instance_filesystem_space_kb_used"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

    def test_wifi_metrics(self):
        """Test WiFi related metrics"""
        # WiFi channel
        metric = Metrics.INSTANCE_WIFI_CHANNEL
        self.assertEqual(metric._name, "wargos_wled_instance_wifi_channel")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # WiFi RSSI
        metric = Metrics.INSTANCE_WIFI_RSSI
        self.assertEqual(metric._name, "wargos_wled_instance_wifi_rssi")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # WiFi signal
        metric = Metrics.INSTANCE_WIFI_SIGNAL
        self.assertEqual(metric._name, "wargos_wled_instance_wifi_signal")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # WiFi BSSID
        metric = Metrics.INSTANCE_WIFI_BSSID
        self.assertEqual(metric._name, "wargos_wled_instance_wifi_bssid")
        self.assertEqual(metric._labelnames, ("name", "ip", "bssid"))

    def test_state_metrics(self):
        """Test state related metrics"""
        # State brightness
        metric = Metrics.INSTANCE_STATE_BRIGHTNESS
        self.assertEqual(metric._name, "wargos_wled_instance_state_brightness")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # State transition
        metric = Metrics.INSTANCE_STATE_TRANSITION
        self.assertEqual(metric._name, "wargos_wled_instance_state_transition")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # State on
        metric = Metrics.INSTANCE_STATE_ON
        self.assertEqual(metric._name, "wargos_wled_instance_state_on")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # State playlist ID
        metric = Metrics.INSTANCE_STATE_PLAYLIST_ID
        self.assertEqual(
            metric._name, "wargos_wled_instance_state_playlist_id"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # State preset ID
        metric = Metrics.INSTANCE_STATE_PRESET_ID
        self.assertEqual(metric._name, "wargos_wled_instance_state_preset_id")
        self.assertEqual(metric._labelnames, ("name", "ip"))

    def test_sync_metrics(self):
        """Test sync related metrics"""
        # Sync receive state
        metric = Metrics.INSTANCE_SYNC_RECEIVE_STATE
        self.assertEqual(
            metric._name, "wargos_wled_instance_sync_receive_state"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Sync send state
        metric = Metrics.INSTANCE_SYNC_SEND_STATE
        self.assertEqual(metric._name, "wargos_wled_instance_sync_send_state")
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Sync receive groups
        metric = Metrics.INSTANCE_SYNC_RECEIVE_GROUPS
        self.assertEqual(
            metric._name, "wargos_wled_instance_sync_receive_groups"
        )
        self.assertEqual(metric._labelnames, ("name", "ip"))

        # Sync send groups
        metric = Metrics.INSTANCE_SYNC_SEND_GROUPS
        self.assertEqual(metric._name, "wargos_wled_instance_sync_send_groups")
        self.assertEqual(metric._labelnames, ("name", "ip"))

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

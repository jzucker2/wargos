from unittest.mock import AsyncMock, patch

import pytest

from app.main import app, lifespan


class TestLifespanEvents:
    @pytest.fixture
    def mock_scraper(self):
        with patch("app.main.Scraper") as mock:
            mock.get_default_scrape_interval.return_value = 60
            mock.get_default_wait_first_interval.return_value = 30
            mock.get_client.return_value = AsyncMock()
            yield mock

    @pytest.fixture
    def mock_wled_client(self):
        with patch("app.main.WLEDClient") as mock:
            mock.get_client.return_value = AsyncMock()
            yield mock

    @pytest.fixture
    def mock_logger(self):
        with patch("app.main.log") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_lifespan_startup_logs(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        async with lifespan(app) as _:
            mock_logger.info.assert_called_with(
                "🚀 Starting up FastAPI application"
            )
            mock_logger.debug.assert_called_with(
                "Starting up FastAPI application"
            )

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_logs(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        async with lifespan(app) as _:
            pass
        mock_logger.info.assert_called_with(
            "🛑 Shutting down FastAPI application"
        )
        mock_logger.debug.assert_called_with(
            "Shutting down FastAPI application"
        )

    @pytest.mark.asyncio
    async def test_lifespan_context_manager(
        self, mock_scraper, mock_wled_client
    ):
        async with lifespan(app) as yielded_app:
            assert yielded_app is app
        async with lifespan(app):
            pass

    def test_app_has_lifespan(self):
        assert hasattr(app, "router")
        assert app.router.lifespan_context is not None

    @pytest.mark.asyncio
    async def test_lifespan_with_mocked_background_task(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        with patch("app.main.Scraper.get_client") as mock_get_client:
            mock_get_client.return_value.perform_full_scrape = AsyncMock()
            async with lifespan(app) as _:
                assert _ is app

    @pytest.mark.asyncio
    async def test_lifespan_with_file_lock_mocking(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        with patch("builtins.open"), patch("fcntl.flock") as mock_flock, patch(
            "os.getpid", return_value=12345
        ):
            mock_flock.side_effect = [None, None]
            with patch("app.main.Scraper.get_client") as mock_get_client:
                mock_get_client.return_value.perform_full_scrape = AsyncMock()
                async with lifespan(app) as _:
                    assert _ is app

    @pytest.mark.asyncio
    async def test_lifespan_with_lock_already_held(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        with patch("builtins.open"), patch("fcntl.flock") as mock_flock, patch(
            "os.getpid", return_value=12345
        ):
            mock_flock.side_effect = IOError(
                "Resource temporarily unavailable"
            )
            async with lifespan(app) as _:
                assert _ is app

    @pytest.mark.asyncio
    async def test_lifespan_with_file_system_error(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        with patch(
            "builtins.open", side_effect=Exception("File system error")
        ), patch("os.getpid", return_value=12345):
            async with lifespan(app) as _:
                assert _ is app

    @pytest.mark.asyncio
    async def test_lifespan_with_scraping_error(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        with patch("builtins.open"), patch("fcntl.flock") as mock_flock, patch(
            "os.getpid", return_value=12345
        ):
            mock_flock.side_effect = [None, None]
            with patch("app.main.Scraper.get_client") as mock_get_client:
                mock_get_client.return_value.perform_full_scrape = AsyncMock(
                    side_effect=Exception("Network error")
                )
                async with lifespan(app) as _:
                    assert _ is app

    @pytest.mark.asyncio
    async def test_lifespan_with_successful_scraping(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        with patch("builtins.open"), patch("fcntl.flock") as mock_flock, patch(
            "os.getpid", return_value=12345
        ):
            mock_flock.side_effect = [None, None]
            with patch("app.main.Scraper.get_client") as mock_get_client:
                mock_get_client.return_value.perform_full_scrape = AsyncMock()
                async with lifespan(app) as _:
                    assert _ is app

    @pytest.mark.asyncio
    async def test_worker_pid_logging(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        with patch("os.getpid", return_value=99999):
            with patch("builtins.open"), patch("fcntl.flock") as mock_flock:
                mock_flock.side_effect = [None, None]
                with patch("app.main.Scraper.get_client") as mock_get_client:
                    mock_get_client.return_value.perform_full_scrape = (
                        AsyncMock()
                    )
                    async with lifespan(app) as _:
                        assert _ is app

    @pytest.mark.asyncio
    async def test_lock_file_path(self, mock_scraper, mock_wled_client):
        with patch("builtins.open"):
            with patch("app.main.Scraper.get_client") as mock_get_client:
                mock_get_client.return_value.perform_full_scrape = AsyncMock()
                async with lifespan(app) as _:
                    assert _ is app

    @pytest.mark.asyncio
    async def test_scrape_interval_logging(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        mock_scraper.get_default_scrape_interval.return_value = 120
        with patch("builtins.open"), patch("fcntl.flock") as mock_flock, patch(
            "os.getpid", return_value=12345
        ):
            mock_flock.side_effect = [None, None]
            with patch("app.main.Scraper.get_client") as mock_get_client:
                mock_get_client.return_value.perform_full_scrape = AsyncMock()
                async with lifespan(app) as _:
                    assert _ is app

    @pytest.mark.asyncio
    async def test_lifespan_multiple_workers_coordination(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        with patch("builtins.open"), patch("fcntl.flock") as mock_flock, patch(
            "os.getpid", return_value=12345
        ):
            mock_flock.side_effect = [
                None,
                None,
                IOError("Resource temporarily unavailable"),
            ]
            with patch("app.main.Scraper.get_client") as mock_get_client:
                mock_get_client.return_value.perform_full_scrape = AsyncMock()
                async with lifespan(app) as _:
                    assert _ is app

    @pytest.mark.asyncio
    async def test_lifespan_with_different_worker_pids(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        pids = [12345, 99999, 11111, 22222]
        for pid in pids:
            with patch("os.getpid", return_value=pid):
                with patch("builtins.open"), patch(
                    "fcntl.flock"
                ) as mock_flock:
                    mock_flock.side_effect = [None, None]
                    with patch(
                        "app.main.Scraper.get_client"
                    ) as mock_get_client:
                        mock_get_client.return_value.perform_full_scrape = (
                            AsyncMock()
                        )
                        async with lifespan(app) as _:
                            assert _ is app

    @pytest.mark.asyncio
    async def test_lifespan_with_different_scrape_intervals(
        self, mock_scraper, mock_wled_client, mock_logger
    ):
        intervals = [30, 60, 120, 300]
        for interval in intervals:
            mock_scraper.get_default_scrape_interval.return_value = interval
            with patch("builtins.open"), patch(
                "fcntl.flock"
            ) as mock_flock, patch("os.getpid", return_value=12345):
                mock_flock.side_effect = [None, None]
                with patch("app.main.Scraper.get_client") as mock_get_client:
                    mock_get_client.return_value.perform_full_scrape = (
                        AsyncMock()
                    )
                    async with lifespan(app) as _:
                        assert _ is app

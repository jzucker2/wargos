import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi_utils.tasks import repeat_every
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    generate_latest,
    multiprocess,
)
from prometheus_fastapi_instrumentator import Instrumentator

from .scraper import Scraper
from .utils import LogHelper
from .version import version
from .wled_client import WLEDClient

log = LogHelper.get_env_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Startup
    log.info("🚀 Starting up FastAPI application")
    log.debug("Starting up FastAPI application")

    # Start the background task
    @repeat_every(
        seconds=Scraper.get_default_scrape_interval(),
        wait_first=Scraper.get_default_wait_first_interval(),
        logger=log,
    )
    async def perform_full_routine_metrics_scrape() -> None:
        import fcntl
        import os

        worker_pid = os.getpid()
        lock_file = "/tmp/wargos_scrape.lock"

        log.info(f"🔄 Background task triggered for worker {worker_pid}")

        try:
            # Try to acquire a file lock to ensure only one worker scrapes
            with open(lock_file, "w") as f:
                try:
                    # Try to acquire an exclusive lock (non-blocking)
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

                    # We got the lock! This worker will do the scraping
                    log.info(
                        f"🔒 Worker {worker_pid}: Acquired scrape lock - performing full scrape"
                    )
                    log.info(
                        f"🔄 Worker {worker_pid}: Performing full scrape of all metrics (interval: {Scraper.get_default_scrape_interval()})"
                    )
                    log.debug(
                        f"Worker {worker_pid}: Going to perform full scrape of all metrics "
                        f"(interval: {Scraper.get_default_scrape_interval()}) "
                        f"=========>"
                    )

                    try:
                        await Scraper.get_client().perform_full_scrape()
                        log.info(
                            f"✅ Worker {worker_pid}: Full scrape completed successfully"
                        )
                    except Exception as e:
                        log.error(
                            f"❌ Worker {worker_pid}: Error during full scrape: {e}"
                        )

                    # Release the lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

                except (IOError, OSError):
                    # Another worker already has the lock
                    log.debug(
                        f"🔒 Worker {worker_pid}: Scrape lock already held by another worker - skipping"
                    )
                    pass

        except Exception as e:
            log.error(f"❌ Worker {worker_pid}: Error with scrape locking: {e}")

    # Start the background task by calling it once to initiate scheduling
    log.info("🔄 Starting background scraping task")
    await perform_full_routine_metrics_scrape()

    # Yield None to keep it running
    yield

    # Shutdown
    log.info("🛑 Shutting down FastAPI application")
    log.debug("Shutting down FastAPI application")


app = FastAPI(lifespan=lifespan)


# Configure Prometheus for multi-worker environments
def configure_prometheus():
    """Configure Prometheus for multi-worker environments"""
    # Check if we're in a multi-process environment
    multiproc_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR")

    if multiproc_dir and os.path.isdir(multiproc_dir):
        # Use multiprocess registry for Gunicorn workers
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)

        # Configure instrumentator with custom registry
        instrumentator = Instrumentator(
            registry=registry,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/metrics"],
            env_var_name="ENABLE_METRICS",
        )

        # Instrument the app
        instrumentator.instrument(app)

        # Add custom metrics endpoint for multiprocess support
        @app.get("/metrics")
        async def metrics():
            """Custom metrics endpoint that aggregates across all workers"""
            return Response(
                generate_latest(registry),
                media_type=CONTENT_TYPE_LATEST,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate"
                },
            )

    else:
        # Use default configuration for single-process environments (like tests)
        instrumentator = Instrumentator(
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/metrics"],
            env_var_name="ENABLE_METRICS",
        )

        # Instrument the app
        instrumentator.instrument(app)


# Configure Prometheus
configure_prometheus()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/healthz")
def healthcheck():
    return {
        "message": "healthy",
        "version": version,
    }


# real stuff here


@app.get("/test")
async def simple_test():
    client = WLEDClient.get_client()
    await client.simple_wled_test()
    return {"message": "Hello World"}


@app.get("/test/releases")
async def simple_releases_test():
    client = WLEDClient.get_client()
    await client.simple_wled_releases_test()
    return {"message": "Hello World"}


@app.get("/prometheus/default")
async def prometheus_default():
    await Scraper.get_client().scrape_default_instance()
    return {"message": "Hello World"}


@app.get("/prometheus/all")
async def prometheus_scrape_all():
    await Scraper.get_client().scrape_all_instances()
    return {"message": "Hello World"}


@app.get("/config/backup/all")
async def backup_configs_all():
    """Backup configs from all WLED instances"""
    results = await Scraper.get_client().backup_configs_from_all_instances()
    return {
        "message": "Config backup completed",
        "results": results,
        "backup_dir": Scraper.get_client().get_config_backup_dir(),
    }


@app.get("/config/backup/{device_ip}")
async def backup_config_single(device_ip: str):
    """Backup config from a single WLED instance"""
    result = await Scraper.get_client().backup_config_from_instance(device_ip)
    return {
        "message": "Config backup completed",
        "result": result,
        "backup_dir": Scraper.get_client().get_config_backup_dir(),
    }


@app.get("/config/backup/all/custom")
async def backup_configs_all_custom(backup_dir: str):
    """Backup configs from all WLED instances to a custom directory"""
    results = await Scraper.get_client().backup_configs_from_all_instances(
        backup_dir
    )
    return {
        "message": "Config backup completed",
        "results": results,
        "backup_dir": backup_dir,
    }


@app.get("/config/download/{device_ip}")
async def download_latest_backup(
    device_ip: str, include_metadata: bool = False
):
    """Download the latest backup file for a specific WLED instance"""
    import json
    import os
    from pathlib import Path

    from fastapi.responses import FileResponse

    from .metrics import Metrics

    backup_dir = Scraper.get_client().get_config_backup_dir()
    ip_backup_dir = Path(backup_dir) / device_ip

    try:
        if not ip_backup_dir.exists():
            # Update metrics for not found
            Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                operation_type="download_latest",
                device_ip=device_ip,
                status="not_found",
            ).inc()

            return {
                "error": f"No backup directory found for device {device_ip}",
                "device_ip": device_ip,
                "status": "not_found",
            }

        # Find the latest backup file
        backup_files = list(ip_backup_dir.glob(f"{device_ip}_*.json"))
        if not backup_files:
            # Update metrics for no files found
            Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
                operation_type="download_latest",
                device_ip=device_ip,
                status="not_found",
            ).inc()

            return {
                "error": f"No backup files found for device {device_ip}",
                "device_ip": device_ip,
                "status": "not_found",
            }

        # Sort by modification time and get the latest
        latest_file = max(backup_files, key=lambda f: f.stat().st_mtime)

        # Read the file content
        with open(latest_file, "r") as f:
            config_data = json.load(f)

        # Strip metadata if not requested
        if not include_metadata and "_backup_metadata" in config_data:
            del config_data["_backup_metadata"]

        # Create a temporary file with the processed content
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            json.dump(config_data, temp_file, indent=2)
            temp_file_path = temp_file.name

        # Update metrics for successful download
        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
            operation_type="download_latest",
            device_ip=device_ip,
            status="success",
        ).inc()

        async def cleanup_temp_file():
            """Clean up the temporary file after response is sent"""
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # File might already be deleted

        return FileResponse(
            path=temp_file_path,
            filename=f"{device_ip}_latest_backup.json",
            media_type="application/json",
            background=cleanup_temp_file,
        )

    except Exception as e:
        # Update metrics for exceptions
        exception_type = type(e).__name__
        Metrics.CONFIG_BACKUP_OPERATIONS_TOTAL.labels(
            operation_type="download_latest",
            device_ip=device_ip,
            status="error",
        ).inc()
        Metrics.CONFIG_BACKUP_OPERATION_EXCEPTIONS.labels(
            operation_type="download_latest",
            device_ip=device_ip,
            exception_type=exception_type,
        ).inc()

        return {
            "error": f"Error downloading backup for device {device_ip}: {str(e)}",
            "device_ip": device_ip,
            "status": "error",
        }

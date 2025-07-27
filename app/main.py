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
    log.debug("Starting up FastAPI application")

    # Start the background task
    @repeat_every(
        seconds=Scraper.get_default_scrape_interval(),
        wait_first=Scraper.get_default_wait_first_interval(),
        logger=log,
    )
    async def perform_full_routine_metrics_scrape() -> None:
        log.debug(
            f"Going to perform full scrape of all metrics "
            f"(interval: {Scraper.get_default_scrape_interval()}) "
            f"=========>"
        )
        await Scraper.get_client().perform_full_scrape()

    # Yield to keep the task running
    yield

    # Shutdown
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
            should_ignore_untemplated=True,
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
            should_ignore_untemplated=True,
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

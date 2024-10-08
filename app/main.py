from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from .version import version

from prometheus_fastapi_instrumentator import Instrumentator


from .utils import LogHelper
from .wled_client import WLEDClient
from .scraper import Scraper


log = LogHelper.get_env_logger(__name__)


app = FastAPI()


Instrumentator().instrument(app).expose(app)


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


@app.on_event("startup")
@repeat_every(
    seconds=Scraper.get_default_scrape_interval(),
    wait_first=Scraper.get_default_wait_first_interval(),
    logger=log,
)
async def perform_full_routine_metrics_scrape() -> None:
    log.debug(f"Going to perform full scrape of all metrics "
              f"(interval: {Scraper.get_default_scrape_interval()}) "
              f"=========>")
    await Scraper.get_client().perform_full_scrape()

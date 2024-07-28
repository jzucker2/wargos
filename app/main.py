from typing import Union

from fastapi import FastAPI
from .version import version

import os
from wled import WLED

from .utils import get_logger


log = get_logger(__name__)


class WLEDClient(object):
    @classmethod
    def default_wled_ip(cls):
        return os.environ.get('DEFAULT_WLED_IP',
                              "10.0.1.179")

    @classmethod
    async def simple_wled_test(cls):
        device_ip = cls.default_wled_ip()
        log.info(f"wled connecting to device_ip: {device_ip}")
        async with WLED(device_ip) as led:
            device = await led.update()
            log.info(f"wled got device: {device}")
            print("device.info.version")
            print(device.info.version)
            print("device.info")
            print(device.info)
            print("device.state")
            print(device.state)

            # Turn strip on, full brightness
            await led.master(on=True, brightness=255)


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/healthz")
def healthcheck():
    return {
        "message": "healthy",
        "version": version,
    }


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# real stuff here


@app.get("/test")
async def simple_test():
    await WLEDClient.simple_wled_test()
    return {"message": "Hello World"}

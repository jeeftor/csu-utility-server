"""Main class."""

import asyncio
import os

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from rich import print

from .const import _LOG
from .csu import CSU

# Extract credentials from enviornment
username = os.getenv("CSU_USERNAME")
password = os.getenv("CSU_PASSWORD")
if not password or not username:
    print("MISSING CREDENTIALS")
    print("Ensure you set CSU_USERNAME and CSU_PASSWORD values")
    exit(1)

csu = CSU(username=username, password=password)
app = FastAPI()


@app.on_event("startup")
@repeat_every(seconds=60 * 30)  # 30 minutes
async def query_gas() -> None:
    """Query gas endpoint."""
    _LOG.info("Downloading energy data")
    asyncio.create_task(csu.download_gas())


@app.get("/gas")
async def gas():
    """Query latest gas entry from sqlite db."""

    return csu.latest_gas

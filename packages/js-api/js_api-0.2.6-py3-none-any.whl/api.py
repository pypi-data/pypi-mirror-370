import tomllib
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

import models
from controllers import docker, health_check, ip
from database import engine

# Read version from pyproject.toml with simplified error handling
try:
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        version = tomllib.load(f)["project"]["version"]
except Exception:
    version = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    docs_url="/docs/swagger",
    redoc_url="/docs/redoc",
    title="Jnstockley API",
    version=version,
    lifespan=lifespan,
    contact={"name": "Jack Stockley"},
    license_info={
        "name": "Apache-2.0",
        "url": "https://opensource.org/license/apache-2-0",
    },
)


app.include_router(health_check.router)
app.include_router(docker.router)
app.include_router(ip.router)

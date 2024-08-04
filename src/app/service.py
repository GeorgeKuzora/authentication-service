import logging

from fastapi import FastAPI

from app.api.handlers import router
from app.api.healthz.handlers import healthz_router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router)
app.include_router(healthz_router)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

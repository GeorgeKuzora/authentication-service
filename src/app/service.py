import logging

from fastapi import FastAPI

from app.api.handlers import router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

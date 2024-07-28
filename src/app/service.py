import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)

app = FastAPI()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

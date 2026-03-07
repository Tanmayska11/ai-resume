import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(funcName)s:%(lineno)d | %(message)s"
)

def setup_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
    )

    # Silence noisy third-party libs
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

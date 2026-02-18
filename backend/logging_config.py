"""
Centralized logging configuration.
- Structured format with level/time/module
- Suppresses noisy third-party loggers
- Uses WARNING in production, INFO in dev
"""
import logging
import os
import sys


def setup_logging() -> None:
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(log_level)
    # Avoid duplicate handlers when uvicorn reloads
    if not root.handlers:
        root.addHandler(handler)
    else:
        root.handlers = [handler]

    # Suppress noisy libraries
    for noisy in (
        "motor",
        "pymongo",
        "asyncio",
        "httpx",
        "websockets",
        "multipart",
        "python_multipart",
        "uvicorn.access",   # access log is already handled by uvicorn
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Keep uvicorn error logs visible
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

import logging
import sys
from functools import wraps
from timeit import default_timer

logger = logging.getLogger("truefoundry.workflow.remote_filesystem")


def init_logger(level=logging.WARNING):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        "[%(name)s] %(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False


def log_time(prefix: str = ""):
    """Decorator to log the time taken by I/O operations."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = default_timer()
            result = func(*args, **kwargs)
            elapsed_time = default_timer() - start_time
            logger.info(f"{prefix}{func.__name__} took {elapsed_time:.2f} seconds")
            return result

        return wrapper

    return decorator

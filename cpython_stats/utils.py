import datetime
import functools
import time
from contextlib import contextmanager

from cpython_stats.logging_utils import set_up_logging

logger = set_up_logging(__name__)


def retry_and_catch(exceptions, tries=5, delay=0, backoff=0):
    """
    Retries function up to amount of tries.

    Backoff disabled by default.

    :param exceptions: List of exceptions to catch
    :param tries: Number of attempts before raising any exceptions
    :param delay: initial delay seconds
    :param backoff: backoff multiplier
    """

    def deco_retry(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            allowed_retries = tries
            current_delay = delay
            exs = tuple(exceptions)
            while allowed_retries > 1:
                try:
                    return f(*args, **kwargs)
                except exs as exception:
                    logger.warning(f"{f.__qualname__} failed execution because of: {exception.__class__}."
                                   f"Retriying in {current_delay} seconds")
                    if current_delay:
                        time.sleep(current_delay)
                        if backoff:
                            current_delay *= backoff
                    allowed_retries -= 1

            return f(*args, **kwargs)

        return f_retry

    return deco_retry


@contextmanager
def session_scope(session):
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise

def cache_response(timeout):
    def decorator(function):
        invalidation_date = None
        cache = functools.lru_cache(maxsize=None)(function)

        def wrapper(*args, **kwargs):
            nonlocal invalidation_date
            if invalidation_date is None or datetime.datetime.now() > invalidation_date:
                cache.cache_clear()
                invalidation_date = datetime.datetime.now() + timeout

            return cache(*args, **kwargs)

        return wrapper
    return decorator

import functools
import logging
import logging.handlers
import os
import threading

import requests


class SimplePushHandler(logging.Handler):
    def __init__(self, simple_push_id, level=logging.NOTSET, asyncronous=False):
        self.id = simple_push_id
        self.asyncronous = asyncronous
        super().__init__(level)

    def emit(self, record):
        url = f"https://api.simplepush.io/send/{self.id}/{record.levelname}/{record.message[:100]}"
        if self.asyncronous:
            thread = threading.Thread(target=requests.get,
                                      args=(url,))
            thread.start()
        else:
            requests.get(url)


def log_on_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.getLogger(__name__).exception(f"{e.__class__.__name__}:{e}")
            raise

    return wrapper


def set_up_logging(name):
    logger = logging.getLogger(name)
    stdout = logging.StreamHandler()
    logger.addHandler(stdout)
    simplepush = SimplePushHandler(os.getenv("SIMPLEPUSH_ID"), level=logging.ERROR)
    logger.addHandler(simplepush)
    logger.setLevel(logging.DEBUG)
    return logger

import logging
import time


def log_decorator(func):
    def wrapper(*args, **kwargs):
        logging.info(f'Started executing: {func.__name__}')
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        logging.info(f'Finished executing: {func.__name__}')
        logging.info(f'Time taken to execute: {end_time - start_time}')

        return result

    return wrapper

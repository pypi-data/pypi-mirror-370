import logging
import time
import functools

class ContextLogger:
    def __init__(self, logger):
        self.logger = logger

    def _log(self, level, msg, *args, **kwargs):
        """
        Custom log function that adds contextual information.
        """
        exc_info = kwargs.get('exc_info', False)  # Avoid passing exc_info multiple times
        kwargs['extra'] = kwargs.get('extra', {})
        kwargs['extra']['context'] = 'MyContext'  # Add any custom context you need

        # Call the standard logging method with proper arguments
        self.logger.log(level, msg, *args, exc_info=exc_info, **kwargs)

    def info(self, msg, *args, **kwargs):
        """ Log at the INFO level. """
        self._log(logging.INFO, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """ Log at the DEBUG level. """
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """ Log at the ERROR level. """
        self._log(logging.ERROR, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """ Log at the WARNING level. """
        self._log(logging.WARNING, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """ Log at the CRITICAL level. """
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    def timeit(self, func):
        """
        A decorator to measure the execution time of a function.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"Function {func.__name__} executed in {duration} seconds")
            return result
        return wrapper

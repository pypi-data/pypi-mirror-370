import logging
import inspect
import time

class ContextLogger(logging.Logger):
    def __init__(self, name, custom_context=None):
        super().__init__(name)
        self.custom_context = custom_context or {}

    def _get_context(self):
        """Helper function to capture context: function name, line number, and local variables."""
        frame = inspect.currentframe().f_back
        return {
            'function': frame.f_code.co_name,
            'line': frame.f_lineno,
            'context': {**self.custom_context, **frame.f_locals}
        }

    def _log(self, level, msg, exc_info=False, exec_time=None):
        """Helper function for logging with context and optional exception info."""
        context = self._get_context()
        exec_time_str = f" | Time Taken: {exec_time:.4f}s" if exec_time else ""
        self.log(level, f"{msg} (Function: {context['function']}, Line: {context['line']}, Context: {context['context']}){exec_time_str}", exc_info=exc_info)

    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def exception(self, msg, *args, **kwargs):
        kwargs['exc_info'] = True
        self._log(logging.ERROR, msg, **kwargs)

def log_context(func):
    """Decorator to log context automatically when function is called, including execution time."""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        start_time = time.time()  # Capture start time
        result = func(*args, **kwargs)
        end_time = time.time()  # Capture end time
        
        exec_time = end_time - start_time  # Calculate execution time
        
        # Log the function execution time along with other context
        logger.debug(f"Executing {func.__name__}", function=func.__name__, args=args, kwargs=kwargs, exec_time=exec_time)
        
        return result
    return wrapper

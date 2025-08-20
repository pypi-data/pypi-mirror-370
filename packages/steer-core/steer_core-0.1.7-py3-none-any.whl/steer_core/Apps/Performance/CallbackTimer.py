from functools import wraps
import time


def timed_callback(func):
    """Time callback execution for optimization."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start

        print(f"CALLBACK: {func.__name__} took {duration:.2f}s")
    
        return result
    return wrapper


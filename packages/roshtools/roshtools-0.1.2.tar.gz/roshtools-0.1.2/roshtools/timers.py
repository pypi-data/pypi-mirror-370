import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Any


class timer:
    def __init__(self, label: str = "Elapsed"):
        self.label = label

    # Context manager support
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        end = time.time()
        print(f"{self.label}: {end - self.start:.4f} seconds")

    # Decorator support
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"{self.label} ({func.__name__}): {end - start:.4f} seconds")
            return result
        return wrapper

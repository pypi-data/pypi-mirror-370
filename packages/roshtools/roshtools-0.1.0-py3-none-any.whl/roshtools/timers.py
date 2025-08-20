import time
from contextlib import contextmanager

@contextmanager
def timer(label: str = "Elapsed"):
    start = time.time()
    yield
    end = time.time()
    print(f"{label}: {end - start:.4f} seconds")

import time
import math
from functools import wraps
from typing import Callable, Any


class timer:
    def __init__(self, label: str = "Elapsed", analyze_complexity: bool = False, samples: int = 6):
        self.label = label
        self.analyze_complexity = analyze_complexity
        self.samples = samples

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
            # Normal timing
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            elapsed = end - start

            if not self.analyze_complexity:
                print(f"{self.label} ({func.__name__}): {elapsed:.4f} seconds")
                return result

            # Complexity analysis (empirical)
            times, sizes = [], []
            for scale in range(1, self.samples + 1):
                new_args = [arg[: len(arg) // self.samples * scale] if hasattr(arg, "__len__") else arg
                            for arg in args]

                s = time.time()
                func(*new_args, **kwargs)
                e = time.time()

                sizes.append(len(new_args[0]) if hasattr(new_args[0], "__len__") else scale)
                times.append(e - s)

            # compute slope of log-log regression manually
            log_sizes = [math.log(s + 1e-9) for s in sizes]
            log_times = [math.log(t + 1e-9) for t in times]

            n = len(log_sizes)
            mean_x = sum(log_sizes) / n
            mean_y = sum(log_times) / n

            numerator = sum((log_sizes[i] - mean_x) * (log_times[i] - mean_y) for i in range(n))
            denominator = sum((log_sizes[i] - mean_x) ** 2 for i in range(n))
            slope = numerator / denominator if denominator != 0 else 0

            # Map slope to Big-O
            if slope < 0.2:
                complexity = "O(1)"
            elif slope < 0.8:
                complexity = "O(log n)"
            elif slope < 1.3:
                complexity = "O(n)"
            elif slope < 1.8:
                complexity = "O(n log n)"
            else:
                complexity = f"O(n^{slope:.2f})"

            print(f"{self.label} ({func.__name__}): {elapsed:.4f} seconds, ~ {complexity}")
            return result

        return wrapper

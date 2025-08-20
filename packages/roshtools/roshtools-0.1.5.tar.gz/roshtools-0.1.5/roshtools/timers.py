import time
import math
import gc
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Any, List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class TimingInfo:
    result: Any
    seconds: float
    complexity: Optional[str]  # None if complexity analysis was not performed
    sizes: Optional[List[int]] = None
    per_call_times: Optional[List[float]] = None
    model_errors: Optional[Dict[str, float]] = None  # RMSE (s) per candidate

    def as_tuple(self):
        return self.result, self.seconds, self.complexity


class timer:
    """
    Use as context manager:
        with timer("Block"):
            ...

    Use as decorator (returns TimingInfo instead of raw result):
        @timer("Work", analyze_complexity=True)
        def f(data): ...
        info = f(big_list)
        print(info.seconds, info.complexity)
    """

    def __init__(
        self,
        label: str = "Elapsed",
        analyze_complexity: bool = False,
        samples: int = 7,
        min_time: float = 0.05,   # target timing per size (s), adaptively loops to reach this
        max_loops: int = 256,     # safety cap on inner repeats
        print_result: bool = True # print timing/complexity to stdout
    ):
        self.label = label
        self.analyze_complexity = analyze_complexity
        self.samples = max(3, samples)
        self.min_time = max(0.0, min_time)
        self.max_loops = max(1, max_loops)
        self.print_result = print_result
        self.elapsed: Optional[float] = None  # available after context exit

    # ---------- Context manager ----------
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        end = time.perf_counter()
        self.elapsed = end - self._start
        if self.print_result:
            print(f"{self.label}: {self.elapsed:.6f} seconds")

    # ---------- Decorator ----------
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Tuple:
            # Single timing first (always)
            start = time.perf_counter()
            res = func(*args, **kwargs)
            elapsed = time.perf_counter() - start

            if not self.analyze_complexity:
                if self.print_result:
                    print(f"{self.label} ({func.__name__}): {elapsed:.6f} seconds")
                return res, elapsed, "O(1)"

            # ---- Complexity analysis (empirical, no numpy/sklearn) ----
            # We’ll vary the size of the FIRST sliceable/len()-able argument.
            idx, base_len = self._find_sized_arg(args)
            if idx is None or base_len < self.samples:
                # Can't analyze; fall back to time only
                if self.print_result:
                    print(f"{self.label} ({func.__name__}): {elapsed:.6f} seconds, ~ (size unknown)")
                return res, elapsed, "O(1)"

            sizes = self._geometric_sizes(base_len, self.samples)

            # Warm-up run (outside timing) to stabilize
            try:
                _ = func(*self._resize_args(args, idx, sizes[0]), **kwargs)
            except Exception:
                pass  # ignore failures during warmup; user function may rely on full size

            per_call_times: List[float] = []
            gc_was_enabled = gc.isenabled()
            try:
                gc.disable()
                for n in sizes:
                    # Adaptively repeat to reach min_time for better signal/noise
                    loops = 1
                    total = 0.0
                    resized = self._resize_args(args, idx, n)
                    while total < self.min_time and loops <= self.max_loops:
                        t0 = time.perf_counter()
                        for _ in range(loops):
                            func(*resized, **kwargs)
                        total = time.perf_counter() - t0
                        if total < self.min_time:
                            loops *= 2
                    per_call = total / max(1, loops)
                    per_call_times.append(per_call)
            finally:
                if gc_was_enabled:
                    gc.enable()

            # Fit against candidate models (with intercept)
            candidates = {
                "O(1)":              lambda x: 1.0,
                "O(log n)":          lambda x: math.log(x),
                "O(n)":              lambda x: float(x),
                "O(n log n)":        lambda x: x * math.log(x),
                "O(n^2)":            lambda x: x**2,
                "O(n^3)":            lambda x: x**3,
                "O(n^4)":            lambda x: x**4,
                "O(n^5)":            lambda x: x**5,
            }

            # Avoid log(0)
            safe_sizes = [max(2, s) for s in sizes]

            errors: Dict[str, float] = {}
            for name, f in candidates.items():
                xs = [f(s) for s in safe_sizes]
                a, b = self._linreg(xs, per_call_times)  # y ≈ a + b*x
                rmse = self._rmse(xs, per_call_times, a, b)
                errors[name] = rmse

            # Choose best model by lowest RMSE
            best_model = min(errors, key=errors.get)
            if self.print_result:
                print(f"{self.label} ({func.__name__}): {elapsed:.6f} seconds, ~ {best_model}")

            return res, elapsed, best_model
        return wrapper

    # ---------- helpers ----------
    @staticmethod
    def _find_sized_arg(args: tuple):
        for i, a in enumerate(args):
            if hasattr(a, "__len__") and hasattr(a, "__getitem__"):
                try:
                    n = len(a)
                    _ = a[:1]
                    return i, n
                except Exception:
                    continue
            # Support integer input for scaling tests
            elif isinstance(a, int) and a > 0:
                return i, a
        return None, None

    @staticmethod
    def _geometric_sizes(max_n: int, samples: int) -> List[int]:
        # geometric schedule from roughly max_n / 2^(samples-1) up to max_n
        sizes = []
        factor = (max_n / 2) ** (1 / (samples - 1))
        val = max(2, int(max_n / 2))
        for _ in range(samples - 1):
            sizes.append(min(max_n, int(val)))
            val *= factor
        sizes.append(max_n)
        # ensure strictly increasing
        sizes = sorted(list(set(sizes)))
        while len(sizes) < samples:
            sizes.append(max_n)
        return sizes

    @staticmethod
    def _resize_args(args: Tuple[Any, ...], idx: int, n: int) -> Tuple[Any, ...]:
        args = list(args)
        sized = args[idx]
        try:
            args[idx] = sized[:n] if hasattr(sized, "__getitem__") else sized
        except Exception:
            args[idx] = sized
        return tuple(args)

    @staticmethod
    def _linreg(x: List[float], y: List[float]) -> Tuple[float, float]:
        # simple linear regression with intercept: y ≈ a + b*x
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        den = sum((x[i] - mean_x) ** 2 for i in range(n))
        b = (num / den) if den != 0 else 0.0
        a = mean_y - b * mean_x
        return a, b

    @staticmethod
    def _rmse(x: List[float], y: List[float], a: float, b: float) -> float:
        n = len(x)
        se = 0.0
        for i in range(n):
            pred = a + b * x[i]
            diff = y[i] - pred
            se += diff * diff
        return (se / n) ** 0.5

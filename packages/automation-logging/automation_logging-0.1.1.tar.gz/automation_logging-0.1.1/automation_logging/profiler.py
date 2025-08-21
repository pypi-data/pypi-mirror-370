import time
import functools
from typing import Callable, Literal, TypeVar, Any

from .global_logger import get_global_log

F = TypeVar("F", bound=Callable[..., Any])


class Profiler:
    def __init__(self, unit: Literal["ns", "ms", "s"] = "s") -> None:
        self.module: str = ""
        self.name: str = ""
        self.unit: Literal["ns", "ms", "s"] = unit
        self.factor: float = {
            "ns": 1.0,
            "ms": 1e-6,
            "s": 1e-9,
        }[unit]
        self.times_called: int = 0
        self.elapsed_time_total: float = 0
        self.elapsed_time_max: float = 0
        self.cpu_time_total: float = 0
        self.cpu_time_max: float = 0

    def __repr__(self):
        msg = (
            f"Function: {self.module}.{self.name}\n"
            f"Times called: {self.times_called}\n"
            f"Elapsed Time (Total: {self.elapsed_time_total} {self.unit}, Avg: {self.elapsed_time_avg} {self.unit}, Max: {self.elapsed_time_max} {self.unit})\n"
            f"CPU Time (Total: {self.cpu_time_total} {self.unit}, Avg: {self.cpu_time_avg} {self.unit}, Max: {self.cpu_time_max} {self.unit}, Ratio: {self.cpu_time_ratio})\n"
        )
        return msg

    def __call__(self, func: F) -> F:
        self.module = func.__module__
        self.name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # if the global log is set, store this Profiler instance
            log = get_global_log()
            if log is not None:
                log.insert_profiler(f"{self.module}.{self.name}", self)

            start_elapsed_time = time.perf_counter_ns()
            start_cpu_time = time.process_time_ns()
            retval = func(*args, **kwargs)
            end_elapsed_time = time.perf_counter_ns()
            end_cpu_time = time.process_time_ns()

            self.times_called += 1

            it_elapsed_time = round((end_elapsed_time - start_elapsed_time) * self.factor, 9)
            it_cpu_time = round((end_cpu_time - start_cpu_time) * self.factor, 9)
            self.elapsed_time_total = round(self.elapsed_time_total + it_elapsed_time, 9)
            self.cpu_time_total = round(self.cpu_time_total + it_cpu_time, 9)
            self.elapsed_time_max = max(self.elapsed_time_max, it_elapsed_time)
            self.cpu_time_max = max(self.cpu_time_max, it_cpu_time)
            if self.cpu_time_max > 1:
                pass
            return retval

        wrapper.__setattr__("profiler", self)
        return wrapper  # pyright: ignore[reportReturnType]

    @property
    def elapsed_time_avg(self) -> float:
        return (
            round(self.elapsed_time_total / self.times_called, 9) if self.times_called > 0 else 0.0
        )

    @property
    def cpu_time_avg(self) -> float:
        return round(self.cpu_time_total / self.times_called, 9) if self.times_called > 0 else 0.0

    @property
    def cpu_time_ratio(self) -> float:
        return (
            round(self.cpu_time_total / self.elapsed_time_total, 9)
            if self.times_called > 0
            else 0.0
        )

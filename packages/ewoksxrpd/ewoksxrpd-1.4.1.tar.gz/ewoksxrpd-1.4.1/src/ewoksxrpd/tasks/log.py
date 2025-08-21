import time
import logging
from contextlib import contextmanager
from typing import Iterator, Optional, Any, Tuple, Generator

from ewoksdata.data.contextiterator import contextiterator

_logger = logging.getLogger(__name__)


@contextiterator
def zip_with_progress(
    *iterators: Iterator[Iterator[Any]],
    message: str = "Progress %d/%s",
    nmax: Optional[int] = None,
    period: float = 5,
    logger=None,
    iter_time_name: str = "iteration",
) -> Generator[Tuple[Any], None, None]:
    """Like python's zip but will progress logging when iterating over the result.
    In addition it yields a context manager which allows for timing different sections
    in the context as well as the yielding time itself:

    .. code::python

        for v1, v2, tmcontext in zip_with_progress([...], [...], iter_time_name="read"):
            with tmcontext("process"):
                ...
            with tmcontext("write"):
                ...
    """
    ctimer = _ContextTimer(iter_time_name)
    if logger is None:
        logger = _logger
    i = 0
    t0 = time.time()
    if nmax is None:
        nmax = "?"
    try:
        for tpl in zip(*iterators):
            yield (*tpl, ctimer.tmcontext)
            i += 1
            if (time.time() - t0) > period:
                t0 = time.time()
                _logger.info(f"{message} (ONGOING: {ctimer})", i, nmax)
    finally:
        _logger.info(f"{message} (FINISHED: {ctimer})", i, nmax)


class _ContextTimer:
    def __init__(self, rest_context: str = "other") -> None:
        self._total_t0 = time.perf_counter_ns()
        self._context_time = dict()
        self._rest_context = rest_context

    @contextmanager
    def tmcontext(self, name: str) -> Generator[None, None, None]:
        context_t0 = time.perf_counter_ns()
        try:
            yield
        finally:
            context_t1 = time.perf_counter_ns()
            self._context_time.setdefault(name, 0)
            self._context_time[name] += context_t1 - context_t0

    def __str__(self) -> str:
        dt_total = time.perf_counter_ns() - self._total_t0
        dt_sum = sum([dt for dt in self._context_time.values()])
        dt_rest = dt_total - dt_sum
        dts = [
            f"{name}={self.strftime(dt, dt_total)}"
            for name, dt in self._context_time.items()
        ]
        dts.append(f"{self._rest_context}={self.strftime(dt_rest, dt_total)}")
        dts.append(f"TOTAL={self.strftime(dt_total, dt_total)}")
        return ", ".join(dts)

    @staticmethod
    def strftime(dt_ns: int, dt_total: int) -> str:
        m, s = divmod(int(dt_ns * 1e-9 + 0.5), 60)
        h, m = divmod(m, 60)
        f = int(dt_ns / dt_total * 100 + 0.5)
        return f"{h:02d}:{m:02d}:{s:02d} ({f:d}%%)"

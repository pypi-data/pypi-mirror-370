import logging
from contextlib import contextmanager
from collections import OrderedDict
from typing import Iterable, Dict, Mapping
from packaging.version import Version

import pyFAI
import pyFAI.worker
from ewokscore.hashing import uhash

from .. import pyfai_api
from .utils import pyfai_utils

_WORKER_POOL = None


logger = logging.getLogger(__name__)


class WorkerPool:
    """Pool with one worker per configuration up to a maximum number of workers."""

    def __init__(self, nworkers: int = 1) -> None:
        self._workers: Dict[int, pyFAI.worker.Worker] = OrderedDict()
        self.nworkers = nworkers

    @staticmethod
    def _worker_id(*args):
        return uhash(args)

    @property
    def nworkers(self):
        return self._nworkers

    @nworkers.setter
    def nworkers(self, value: int):
        self._nworkers = value
        self._check_pool_size()

    def _check_pool_size(self):
        while self._workers and len(self._workers) > self.nworkers:
            self._workers.popitem(last=False)

    @contextmanager
    def worker(
        self, ewoks_pyfai_options: Mapping, demo: bool = False
    ) -> Iterable[pyFAI.worker.Worker]:
        # TODO: deal with threads and subprocesses
        worker_options, integration_options = (
            pyfai_utils.split_worker_and_integration_options(ewoks_pyfai_options)
        )
        logger.info("Pyfai worker options: %s", worker_options)
        logger.info("Pyfai integration options: %s", integration_options)

        worker_id = self._worker_id(worker_options, integration_options, demo)
        worker = self._workers.pop(worker_id, None)
        if worker is None:
            logger.info("Creating a new pyfai worker")
            worker = self._create_worker(worker_options, integration_options, demo)
        self._workers[worker_id] = worker

        self._check_pool_size()
        logger.info("Pyfai integration method: %s", worker._method)
        yield worker

    @staticmethod
    def _create_worker(
        worker_options: Mapping, integration_options: Mapping, demo: bool
    ) -> pyFAI.worker.Worker:
        if demo:
            return DemoWorker(integration_options, worker_options)
        return EwoksWorker(integration_options, worker_options)


def _get_global_pool() -> WorkerPool:
    global _WORKER_POOL
    if _WORKER_POOL is None:
        _WORKER_POOL = WorkerPool()
    return _WORKER_POOL


def set_maximum_persistent_workers(nworkers: int) -> None:
    pool = _get_global_pool()
    pool.nworkers = nworkers


class EwoksWorker(pyFAI.worker.Worker):
    def __init__(self, integration_options: Mapping, worker_options: Mapping) -> None:
        super().__init__(**worker_options)
        self.output = "raw"
        self._i = 0

        integration_options, mask, flatfield, darkcurrent = (
            pyfai_utils.extract_images_from_integration_options(integration_options)
        )

        provided = set(integration_options)
        self.set_config(integration_options, consume_keys=True)
        unused = {k: v for k, v in integration_options.items() if k in provided}
        if unused:
            logger.warning("Unused pyFAI integration options: %s", unused)
        else:
            logger.info("All pyFAI integration options were used")

        # Flat/dark correction:
        #   Icor = (I - darkcurrent) / flatfield
        if mask is not None:
            self.ai.detector.set_mask(mask)
        if flatfield is not None:
            self.ai.detector.set_flatfield(flatfield)
        if darkcurrent is not None:
            self.ai.detector.set_darkcurrent(darkcurrent)

    def set_config(self, integration_options, consume_keys=False):
        if pyfai_api.PYFAI_VERSION < Version("2025.1.0"):
            # In older pyFAI versions, the "method" is required
            # when upgrading version 2 to 3.
            version = integration_options.get("version", 1)

            if version == 2:
                if self.integrator_name and "clip" in self.integrator_name:
                    method = "csr"
                else:
                    method = ""
                integration_options["method"] = method

        super().set_config(integration_options, consume_keys=consume_keys)


class DemoWorker(EwoksWorker):
    def process(self, data, *args, **kwargs):
        return super().process(data[:-1, :-1], *args, **kwargs)


@contextmanager
def persistent_worker(
    ewoks_pyfai_options: Mapping, demo: bool = False
) -> Iterable[pyFAI.worker.Worker]:
    """Get a worker for a particular configuration that stays in memory."""
    pool = _get_global_pool()
    with pool.worker(ewoks_pyfai_options, demo) as worker:
        yield worker

from abc import ABC, abstractmethod
from typing import Optional

from behave.model import Feature
from behave.runner import Runner as BehaveRunner
from behave.runner import Context
from behave.formatter._registry import make_formatters
from behave.runner import the_step_registry as behave_step_registry

from behave.configuration import Configuration

from ..pool import PoolExecutor


class WorkerRunner(BehaveRunner):
    """Runner subclass for executing features inside a worker
    (thread/process).

    Behaviour:
    - Initializes one `Context` per worker (created once in `start()`).
    - Loads hooks and step definitions once.
    - Exposes `run_feature()` to execute features dynamically, one by one.
    - `finish()` finalizes the run (after_all, cleanups, formatter close,
      reporter end).
    """

    _is_started: bool
    _is_finished: bool
    _is_failed: bool
    _index: int

    def __init__(self, config: Configuration, index: int):
        super().__init__(config)
        self._is_started = False
        self._is_finished = False
        self._is_failed = False
        self._index = index

    @property
    def index(self) -> int:
        return self._index

    def __str__(self):
        return f"{self.__class__.__name__}-{self.index}"

    def __repr__(self) -> str:
        return "self[%s]" % self.__str__()

    def setup(self) -> None:
        """Prepare the worker runner once per worker.

        - Setup paths
        - Create `Context`
        - Load hooks and step definitions
        - Initialize formatters
        - Run `before_all`
        """
        if self._is_started:
            return
        # Setup import paths and base_dir similar to Behave's `run()`
        self.setup_paths()

        # Create fresh context for this worker and preload hooks/steps
        self.context = Context(self)
        self.step_registry = self.step_registry or behave_step_registry
        self.load_hooks()
        self.load_step_definitions()

        # Initialize formatters once per worker
        stream_openers = self.config.outputs
        self.formatters = make_formatters(self.config, stream_openers)

        # Run before_all hook once per worker
        self.hook_failures = 0
        self.run_hook("before_all")
        self._is_started = True

    def run_feature(self, feature: Optional[Feature]) -> None:
        """Run a single Feature with the worker's context"""
        self.setup()

        if feature is None:
            self.teardown()
            return

        is_failed = False
        if not (self.aborted or self.config.stop):
            try:
                self.feature = feature
                for formatter in self.formatters:
                    formatter.uri(feature.filename)

                is_failed = feature.run(self)
            except KeyboardInterrupt:
                self.abort(reason="KeyboardInterrupt")
                is_failed = True

        for reporter in self.config.reporters:
            reporter.feature(feature)

        self._is_failed |= is_failed

    def teardown(self) -> None:
        """Finalize the worker run"""
        if not self._is_started or self._is_finished:
            return
        cleanups_failed = False
        self.run_hook_with_capture("after_all")
        try:
            self.context._do_remaining_cleanups()
        except Exception:
            cleanups_failed = True

        if self.aborted:
            print("\nABORTED: By user.")
        for formatter in self.formatters:
            formatter.close()
        for reporter in self.config.reporters:
            reporter.end()

        self._is_failed = (
            self.is_failed
            or self.aborted
            or (self.hook_failures > 0)
            or (len(self.undefined_steps) > 0)
            or cleanups_failed
        )

        self._is_finished = True

    @property
    def is_failed(self) -> bool:
        return self._is_failed


class Worker(ABC):

    _runner: WorkerRunner

    def __init__(self, config: Configuration, index: int):
        self._runner = WorkerRunner(config, index)

    def __str__(self):
        return f"{self.__class__.__name__}-{self.index}"

    def __repr__(self) -> str:
        return "self[%s]" % self.__str__()

    @property
    def runner(self) -> WorkerRunner:
        return self._runner

    @property
    def index(self) -> int:
        return self.runner.index

    @abstractmethod
    def run_feature(self, feature: Optional[Feature]) -> None:
        pass

    @abstractmethod
    def done(self) -> bool:
        pass

    def shutdown(self):
        pass


class WorkerPoolExecutor(PoolExecutor[Worker]):

    def __init__(self, config: Configuration, worker_class: type):
        super().__init__(config, worker_class)

    def done(self) -> bool:
        for worker in self:
            if not worker.done():
                return False
        return True

    def __enter__(self) -> "WorkerPoolExecutor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for worker in self._pool:
            worker.shutdown()

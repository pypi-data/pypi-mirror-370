from time import sleep
from behave.configuration import Configuration
from behave.model import Step
from behave.runner import ITestRunner
from behave.runner_util import PathManager

from .task import FeatureTaskAllocator, TaskAllocator
from .workers import WorkerPoolExecutor
from .workers.thread import ThreadWorker


class ParallelRunner(ITestRunner):

    config: Configuration
    task_allocator: TaskAllocator
    worker_pool_executor: WorkerPoolExecutor

    def __init__(
        self,
        config: Configuration,
        task_allocator: TaskAllocator,
        worker_pool_executor: WorkerPoolExecutor,
    ):
        super().__init__(config)
        self.task_allocator = task_allocator
        self.worker_pool_executor = worker_pool_executor

    def run(self) -> bool:
        with PathManager():
            with self.worker_pool_executor as pool:
                while not (self.task_allocator.empty() and pool.done()):
                    for index, worker in enumerate(pool):
                        if worker.done():
                            feature = self.task_allocator.allocate(index)
                            worker.run_feature(feature)
                    sleep(0.01)
            return any(worker.runner.is_failed for worker in self.worker_pool_executor)

    @property
    def undefined_steps(self) -> list[Step]:
        return [
            step
            for worker in self.worker_pool_executor
            for step in worker.runner.undefined_steps
        ]


class FeatureParallelRunner(ParallelRunner):

    def __init__(self, config: Configuration):
        super().__init__(
            config=config,
            task_allocator=FeatureTaskAllocator(config),
            worker_pool_executor=WorkerPoolExecutor(config, ThreadWorker),
        )


ITestRunner.register(FeatureParallelRunner)

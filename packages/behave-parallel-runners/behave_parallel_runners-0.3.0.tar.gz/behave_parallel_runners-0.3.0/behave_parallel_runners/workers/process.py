import os
from typing import Optional
from multiprocessing import Process, JoinableQueue

from behave.model import Feature
from behave.configuration import Configuration

from . import Worker


class ProcessWorker(Worker):

    _process: Process
    _task_queue: JoinableQueue

    def __init__(self, config: Configuration, index: int):
        super().__init__(config, index)
        self._process = Process(
            target=self._process_loop,
            args=(os.environ,),
            name=str(self),
            daemon=True,
        )
        self._task_queue = JoinableQueue()
        self._process.start()

    def run_feature(self, feature: Optional[Feature]) -> None:
        self._task_queue.put_nowait(feature)

    def done(self) -> bool:
        return (
            not self._process.is_alive()
            or self._task_queue._unfinished_tasks._semlock._is_zero()
        )

    def shutdown(self):
        if self._process.is_alive():
            self._task_queue.put(None)
            while not self.done():
                pass
            self._process.terminate()
            self._process.join()
        self._task_queue.close()

    def _process_loop(self, envs):
        os.environ = envs
        while True:
            feature = self._task_queue.get()

            self.runner.run_feature(feature)
            self._task_queue.task_done()

            if self.runner._is_finished:
                break

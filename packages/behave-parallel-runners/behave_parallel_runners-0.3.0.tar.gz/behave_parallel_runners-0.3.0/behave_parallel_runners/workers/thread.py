from typing import Optional
from threading import Thread
from queue import Queue

from behave.model import Feature
from behave.configuration import Configuration

from . import Worker


class ThreadWorker(Worker):

    _thread: Thread
    _task_queue: Queue

    def __init__(self, config: Configuration, index: int):
        super().__init__(config, index)
        self._thread = self._thread = Thread(
            target=self._thread_loop,
            name=str(self),
            daemon=True,
        )
        self._task_queue = Queue()
        self._thread.start()

    def run_feature(self, feature: Optional[Feature]) -> None:
        self._task_queue.put_nowait(feature)

    def done(self) -> bool:
        return not self._thread.is_alive() or self._task_queue.unfinished_tasks == 0

    def shutdown(self):
        self.run_feature(None)
        self._thread.join()
        self._task_queue.shutdown()

    def _thread_loop(self):
        while True:
            feature = self._task_queue.get()

            self.runner.run_feature(feature)
            self._task_queue.task_done()

            if self.runner._is_finished:
                break

from typing import Optional
from concurrent.interpreters import create, Interpreter

from behave.model import Feature
from behave.configuration import Configuration

from . import Worker


class InterpreterWorker(Worker):

    _interpreter: Interpreter

    def __init__(self, config: Configuration, index: int):
        super().__init__(config, index)
        self._interpreter = create()

    def run_feature(self, feature: Optional[Feature]) -> None:
        self._interpreter.call(self.runner.run_feature, feature)

    def done(self) -> bool:
        return not self._interpreter.is_running()

    def shutdown(self) -> None:
        self.run_feature(None)
        while not self.done():
            pass
        self._interpreter.close()

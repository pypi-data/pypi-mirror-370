from abc import ABC
from typing import Generator, TypeVar, Generic

from behave.configuration import Configuration

T = TypeVar("T")


class PoolExecutor(ABC, Generic[T]):

    _config: Configuration
    _pool: list[T]

    def __init__(self, config: Configuration, item_class: type[T]):
        self._config = config
        self._pool = self._init_items(item_class)

    def _init_items(self, item_class: type[T]) -> list[T]:
        return [item_class(self._config, index) for index in range(self._config.jobs)]

    def __getitem__(self, index: int) -> T:
        return self._pool[index]

    def __iter__(self) -> Generator[T]:
        for worker in self._pool:
            yield worker

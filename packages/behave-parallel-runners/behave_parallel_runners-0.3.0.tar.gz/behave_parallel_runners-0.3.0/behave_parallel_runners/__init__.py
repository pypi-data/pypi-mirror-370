import sys

from behave.model import Tag
from behave.formatter.base import StreamOpener
from behave.reporter.summary import AbstractSummaryReporter

# For multiprocessing pickle configuration

# SummaryReporter


def reporter_getstate(self):
    """Исключает self.stream из сериализуемых данных."""
    state = self.__dict__.copy()
    if "stream" in state:
        del state["stream"]  # Удаляем несериализуемый атрибут
    return state


def reporter_setstate(self, state):
    """Восстанавливает состояние и пересоздаёт self.stream."""
    self.__dict__.update(state)
    # Пересоздаём поток на основе сохранённого имени (output_stream_name)
    stream = getattr(sys, self.output_stream_name, sys.stdout)
    self.stream = StreamOpener.ensure_stream_with_encoder(stream)


AbstractSummaryReporter.__getstate__ = reporter_getstate
AbstractSummaryReporter.__setstate__ = reporter_setstate


# Tag


def tag_getstate(self):
    # Сохраняем состояние: значение строки и дополнительный атрибут
    return (super(Tag, self).__str__(), self.line)


def tag_reduce(self):
    # Указываем, как создать объект при десериализации
    return (Tag, (super(Tag, self).__str__(), self.line))


Tag.__getstate__ = tag_getstate
Tag.__reduce__ = tag_reduce

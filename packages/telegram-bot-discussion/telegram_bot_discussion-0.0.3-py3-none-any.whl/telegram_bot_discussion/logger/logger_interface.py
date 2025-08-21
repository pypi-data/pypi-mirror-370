from abc import ABC, abstractmethod


class LoggerInterface(ABC):

    @abstractmethod
    def debug(self, *args, **kwargs): ...

    @abstractmethod
    def info(self, *args, **kwargs): ...

    @abstractmethod
    def warning(self, *args, **kwargs): ...

    @abstractmethod
    def error(self, *args, **kwargs): ...

    def __call__(self, *args, **kwargs):
        self.info(*args, **kwargs)

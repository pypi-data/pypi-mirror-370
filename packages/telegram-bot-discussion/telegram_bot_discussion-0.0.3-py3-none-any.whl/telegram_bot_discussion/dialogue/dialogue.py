from abc import ABC, abstractmethod
from typing import Any, Generator, Union


from telegram import Update

from .replicas.base import EmptyReplica, Replica, StopReplica


Phrase = Generator[
    Replica,
    Update,
    Any,
]

Polemic = Generator[
    Union[
        Replica,
        StopReplica,
    ],
    Update,
    None,
]


class Dialogue(ABC):
    @abstractmethod
    def dialogue(self, *args, **kwargs) -> Polemic: ...

    def replicas_flow(self, *args, **kwargs) -> Polemic:
        _ = yield EmptyReplica()
        return (yield from self.dialogue(*args, **kwargs))

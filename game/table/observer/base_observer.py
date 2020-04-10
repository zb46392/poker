from abc import ABC, abstractmethod
from . import State


class BaseObserver(ABC):
    @abstractmethod
    def update(self, state: State) -> None:
        pass

from .observer import BaseObserver as Observer, State
from typing import List


class Observers:
    def __init__(self) -> None:
        self._observers = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        for i in range(len(self._observers)):
            if self._observers[i] == observer:
                self._observers.pop(i)

    def notify(self, state: State) -> None:
        for observer in self._observers:
            observer.update(state)

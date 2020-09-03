from .observer import BaseObserver as Observer, State


class Observers:
    def __init__(self) -> None:
        self._observers = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        detached = 0

        for i in range(len(self._observers)):
            if self._observers[i - detached] == observer:
                self._observers.pop(i - detached)
                detached += 1

    def notify(self, state: State) -> None:
        for observer in self._observers:
            observer.update(state)

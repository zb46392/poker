from . import InterpretableState
from abc import ABC, abstractmethod
from game.deck import Deck
from game.moves import Moves
from typing import List


class Base(ABC):
    def __init__(self) -> None:
        self._deck = Deck()

    @property
    @abstractmethod
    def state_space(self) -> int:
        pass

    @property
    def action_space(self) -> int:
        return len(Moves)

    def interpret(self, state: InterpretableState) -> List[float]:
        return self._generate_interpreted_state(state)

    @abstractmethod
    def _generate_interpreted_state(self, state: InterpretableState) -> List[float]:
        pass

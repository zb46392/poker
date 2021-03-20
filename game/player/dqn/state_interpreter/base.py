from abc import ABC, abstractmethod
from game.deck import Deck
from game.moves import Moves
from game.player import Player
from game.state import State
from typing import List


class Base(ABC):
    def __init__(self, player: Player) -> None:
        self._player = player
        self._starting_chips_amount = self._player.get_amount_of_chips()
        self._total_chips_amount = None
        self._deck = Deck()

    @property
    def total_chips_amount(self) -> int:
        return self._total_chips_amount

    @property
    @abstractmethod
    def state_space(self) -> int:
        pass

    @property
    def action_space(self) -> int:
        return len(Moves)

    def interpret(self, state: State) -> List[float]:
        if self._total_chips_amount is None:
            self._determine_total_chips_amount(state)

        return self._generate_interpreted_state(state)

    def _determine_total_chips_amount(self, state: State) -> None:
        self._total_chips_amount = state.total_nbr_of_players * self._starting_chips_amount

    @abstractmethod
    def _generate_interpreted_state(self, state: State) -> List[float]:
        pass

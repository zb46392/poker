from abc import ABC, abstractmethod
from game import Card, Moves, State
from typing import List, Optional


class Player(ABC):
    def __init__(self, chips: int, name: Optional[str] = None) -> None:
        self._chips = chips
        self._hand = []
        self._wager = 0
        if name is None:
            name = type(self).__name__
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def wager(self) -> int:
        return self._wager

    def receive_chips(self, amount: int) -> None:
        self._chips += amount
        self._wager = 0

    def spend_chips(self, amount: int) -> int:
        self._chips -= amount
        self._wager += amount
        return amount

    def receive_cards(self, cards: List[Card]) -> None:
        self._hand += cards

    def get_hand(self) -> List[Card]:
        return self._hand

    def destroy_hand(self) -> None:
        self._hand = []

    def get_amount_of_chips(self) -> int:
        return self._chips

    @abstractmethod
    def make_move(self, possible_moves: List[Moves], game_state: State) -> Moves:
        pass

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self):
        return str(self)

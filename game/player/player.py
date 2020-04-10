from abc import ABC, abstractmethod
from game import Card, Moves, State
from typing import List


class Player(ABC):
    def __init__(self, chips: int) -> None:
        self._chips = chips
        self._hand = []

    def receive_chips(self, amount: int) -> None:
        self._chips += amount

    def spend_chips(self, amount: int) -> int:
        self._chips -= amount
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

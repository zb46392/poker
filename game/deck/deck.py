from .card import Card
from random import shuffle
from typing import List

RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace')
SUITS = ('Heart', 'Diamond', 'Spade', 'Club')


class Deck:

    def __init__(self) -> None:
        self.cards = [Card(rank, suit, value + 1) for rank, value in zip(RANKS, range(len(RANKS))) for suit in SUITS]

    def shuffle(self) -> None:
        shuffle(self.cards)

    def deal(self, amount: int = 1) -> List[Card]:
        to_deal = self.cards[:amount]
        self.cards = self.cards[amount:]

        return to_deal

    def burn(self, amount: int = 1) -> None:
        self.cards = self.cards[amount:]

    def create_new_deck(self) -> None:
        self.__init__()

    def get_cards(self) -> List[Card]:
        return self.cards

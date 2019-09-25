from .card import Card
from random import shuffle

RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace')
SUITS = ('Heart', 'Diamond', 'Spade', 'Club')


class Deck:

    def __init__(self):
        self.cards = [Card(rank, suit, value+1) for rank, value in zip(RANKS, range(len(RANKS))) for suit in SUITS]

    def shuffle(self):
        shuffle(self.cards)

    def deal(self, amount):
        to_deal = self.cards[:amount]
        self.cards = self.cards[amount:]

        return to_deal

    def burn(self, amount):
        self.cards = self.cards[amount:]

    def create_new_deck(self):
        self.__init__()

    def get_cards(self):
        return self.cards

from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, chips: int):
        self.chips = chips
        self.hand = []

    def receive_chips(self, amount: int):
        self.chips += amount

    def spend_chips(self, amount: int):
        self.chips -= amount
        return amount

    def receive_cards(self, cards: list):
        self.hand += cards

    def get_hand(self):
        return self.hand

    def destroy_hand(self):
        self.hand = []

    def get_amount_of_chips(self):
        return self.chips

    @abstractmethod
    def make_move(self, possible_moves, game_state):
        pass

class Player:
    def __init__(self, chips):
        self.chips = chips
        self.hand = []

    def receive_chips(self, amount):
        self.chips += amount

    def spend_chips(self, amount):
        self.chips -= amount
        return amount

    def receive_card(self, card):
        self.hand.append(card)

    def show_hand(self):
        return self.hand

    def burn_hand(self):
        self.hand = []

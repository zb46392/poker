class Card:
    def __init__(self, rank, suit, value):
        self.rank = rank
        self.suit = suit
        self.value = value

    def get_rank(self):
        return self.rank

    def get_suit(self):
        return self.suit

    def get_value(self):
        return self.value

    def __str__(self):
        return str(self.get_rank()) + '(' + str(self.get_suit() + ')')

    def __eq__(self, other):
        return self.value == other.get_value() and self.suit == other.get_suit()

    def __lt__(self, other):
        return self.value < other.get_value()

    def __gt__(self, other):
        return self.value > other.get_value()

    def __repr__(self):
        return str(self)

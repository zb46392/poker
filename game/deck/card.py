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
        return str(self.get_rank()) + '(' + str(self.get_suit() + ')::' +
                                                (12 - (len(self.get_suit()) + len(self.get_rank()))) * ' ' +
                                                str(self.get_value()))

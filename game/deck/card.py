class Card:
    def __init__(self, rank: str, suit: str, value: int) -> None:
        self._rank = rank
        self._suit = suit
        self._value = value

    @property
    def rank(self) -> str:
        return self._rank

    @property
    def suit(self) -> str:
        return self._suit

    @property
    def value(self) -> int:
        return self._value

    def __str__(self) -> str:
        return str(self._rank) + '(' + str(self._suit + ')')

    def __eq__(self, other) -> bool:
        return self._value == other.value and self._suit == other.suit

    def __lt__(self, other) -> bool:
        return self._value < other.value

    def __gt__(self, other) -> bool:
        return self._value > other.value

    def __repr__(self) -> str:
        return str(self)

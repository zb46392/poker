from ..players import Players
from game import Card
from typing import List, NamedTuple


class State(NamedTuple):
    players: Players
    community_cards: List[Card]
    pot: int
    phase: str

from ..players import Players
from game import Card, Phases
from typing import List, NamedTuple


class State(NamedTuple):
    players: Players
    community_cards: List[Card]
    pot: int
    phase: Phases
    is_game_active: bool

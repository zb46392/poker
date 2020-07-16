from game import Card, Phases
from typing import NamedTuple, List


class State(NamedTuple):
    community_cards: List[Card]
    nbr_of_players: int
    current_phase: Phases

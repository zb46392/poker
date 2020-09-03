from game import Card, Phases
from typing import NamedTuple, List


class State(NamedTuple):
    community_cards: List[Card]
    total_nbr_of_players: int
    nbr_of_active_players: int
    current_phase: Phases
    is_raising_capped: bool

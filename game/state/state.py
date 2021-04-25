from game import Card, Phases, Moves
from typing import NamedTuple, Tuple


class State(NamedTuple):
    community_cards: Tuple[Card, ...]
    total_players: int
    total_chips: int
    pot: int
    nbr_of_active_players: int
    current_phase: Phases
    is_raising_capped: bool
    allowed_moves: Tuple[Moves, ...]
    current_bet: int

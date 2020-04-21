from ..players import Players
from game import Card, Phases
from typing import Dict, List, NamedTuple


class State(NamedTuple):
    players: Players
    community_cards: List[Card]
    pot: int
    phase: Phases
    individual_pot_collection: Dict[Players, int]

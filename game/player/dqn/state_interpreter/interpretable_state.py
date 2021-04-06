from game import State as GameState, Card
from typing import NamedTuple, Tuple


class InterpretableState(NamedTuple):
    game_state: GameState
    hand: Tuple[Card, ...]
    current_chips_amount: int
    initial_chips_amount: int

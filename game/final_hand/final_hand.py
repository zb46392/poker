from . import FinalHandType
from game import Card
from typing import List, NamedTuple


class FinalHand(NamedTuple):
    hand: List[Card]
    type: FinalHandType
    score: int

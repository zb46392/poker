from . import Player
from game import Moves, State
from typing import List


class Dummy(Player):
    def make_move(self, possible_moves: List[Moves], game_state: State) -> Moves:
        return possible_moves[0]

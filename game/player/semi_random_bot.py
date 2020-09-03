from . import Player
from game import Moves, State
from random import shuffle
from typing import List, Optional


class SemiRandomBot(Player):
    def make_move(self, possible_moves: List[Moves], game_state: Optional[State]) -> Moves:
        shuffle(possible_moves)

        if Moves.CHECK in possible_moves and possible_moves[0] is Moves.FOLD:
            return Moves.CHECK
        else:
            return possible_moves[0]

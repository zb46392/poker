from . import Player
from game import Moves, State
from random import shuffle
from typing import List


class RandomBot(Player):
    def make_move(self, possible_moves: List[Moves], game_state: State) -> Moves:
        shuffle(possible_moves)

        return possible_moves[0]

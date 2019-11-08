from game import Player


class Dummy(Player):

    def make_move(self, possible_moves, game_state):
        return possible_moves[0]


def create_dummy_classes(amount):
    return [Dummy for _ in range(amount)]

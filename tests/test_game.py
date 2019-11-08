from unittest import TestCase
from game import Table
from . import create_dummy_classes


class TestGame(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.table = Table(create_dummy_classes(3))
        self.player_1 = self.table.get_dealer()
        self.player_2 = self.table.get_next_player(self.player_1)
        self.player_3 = self.table.get_next_player(self.player_2)

        self.moves = self.table.Moves

    def reset(self):
        self.__init__()

from unittest import TestCase
from game import Moves, Table
from .dummy_player import create_dummy_classes


class TestGame(TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        Table.INIT_CHIPS = 100

        self.table = Table(create_dummy_classes(3))

        self.player_1 = self.table._players
        self.player_2 = self.player_1.next
        self.player_3 = self.player_2.next

        self.moves = Moves

    def reset(self):
        self.__init__()

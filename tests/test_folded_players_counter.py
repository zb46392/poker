from . import TestGame
from game import Moves


class TestFoldedPlayersCounter(TestGame):
    def test_folded_players_counter(self) -> None:

        self.assertEqual(0, len(self.player_1.find_by_move(Moves.FOLD)))
        self.table.execute_player_move(self.player_1, self.moves.FOLD)
        self.assertEqual(1, len(self.player_1.find_by_move(Moves.FOLD)))
        self.table.execute_player_move(self.player_2, self.moves.FOLD)
        self.assertEqual(2, len(self.player_2.find_by_move(Moves.FOLD)))
        self.table.execute_player_move(self.player_3, self.moves.FOLD)
        self.assertEqual(3, len(self.player_3.find_by_move(Moves.FOLD)))

    def test_have_all_players_folded_but_one(self) -> None:

        self.assertTrue(self.table._is_round_active)
        self.table.execute_player_move(self.player_1, self.moves.FOLD)
        self.table.update_round_active_state()
        self.assertTrue(self.table._is_round_active)
        self.table.execute_player_move(self.player_2, self.moves.FOLD)
        self.table.update_round_active_state()
        self.assertFalse(self.table._is_round_active)

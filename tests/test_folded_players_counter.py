from . import TestGame


class TestFoldedPlayersCounter(TestGame):
    def test_folded_players_counter(self) -> None:

        self.assertEqual(0, self.table.count_folded_players())
        self.table.execute_player_move(self.player_1, self.moves.FOLD)
        self.assertEqual(1, self.table.count_folded_players())
        self.table.execute_player_move(self.player_2, self.moves.FOLD)
        self.assertEqual(2, self.table.count_folded_players())
        self.table.execute_player_move(self.player_3, self.moves.FOLD)
        self.assertEqual(3, self.table.count_folded_players())

    def test_have_all_players_folded_but_one(self) -> None:

        self.assertFalse(self.table.have_all_folded_but_one())
        self.table.execute_player_move(self.player_1, self.moves.FOLD)
        self.assertFalse(self.table.have_all_folded_but_one())
        self.table.execute_player_move(self.player_2, self.moves.FOLD)
        self.assertTrue(self.table.have_all_folded_but_one())

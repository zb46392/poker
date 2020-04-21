from . import TestGame


class TestPlayerMovesGenerator(TestGame):
    def prepare_game(self) -> None:
        self.table._deck.shuffle()
        self.table.deal_cards()
        self.table.collect_blinds()
        self.table._current_raise = self.table._current_bet = self.table._small_bet

    def test_moves_after_big_blind_player(self) -> None:
        self.prepare_game()

        self.assertEqual([self.moves.CALL, self.moves.RAISE, self.moves.FOLD],
                         self.table.generate_player_moves(self.player_1))

    def test_moves_big_blind_player(self) -> None:
        self.prepare_game()

        self.assertEqual([self.moves.CHECK, self.moves.RAISE, self.moves.FOLD],
                         self.table.generate_player_moves(self.player_3))

    def test_capped_reraise(self) -> None:
        self.prepare_game()

        self.table.execute_player_move(self.player_1, self.moves.RAISE)
        self.table.execute_player_move(self.player_2, self.moves.RAISE)
        self.table.execute_player_move(self.player_3, self.moves.RAISE)
        self.table.execute_player_move(self.player_1, self.moves.RAISE)

        self.assertEqual([self.moves.CALL, self.moves.FOLD], self.table.generate_player_moves(self.player_2))

    def test_higher_bet_than_player_chips(self) -> None:
        self.prepare_game()
        self.player_1.spend_chips(95)

        self.assertEqual([self.moves.CALL, self.moves.RAISE, self.moves.FOLD],
                         self.table.generate_player_moves(self.player_1))

        for _ in range(2):
            self.player_1.spend_chips(1)
            self.assertEqual([self.moves.CALL, self.moves.ALL_IN, self.moves.FOLD],
                             self.table.generate_player_moves(self.player_1))

        for _ in range(2):
            self.player_1.spend_chips(1)
            self.assertEqual([self.moves.ALL_IN, self.moves.FOLD], self.table.generate_player_moves(self.player_1))

    def test_no_moves_left(self) -> None:
        self.prepare_game()
        self.table.execute_player_move(self.player_1, self.moves.FOLD)

        self.assertEqual(None, self.table.generate_player_moves(self.player_1))

        self.table.execute_player_move(self.player_2, self.moves.ALL_IN)
        self.assertEqual(None, self.table.generate_player_moves(self.player_2))

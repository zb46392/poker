from . import TestGame
from .dummy_player import create_dummy_classes
from game import Table, Moves


class TestIsRoundActive(TestGame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        Table.INIT_CHIPS = 10
        self.table = Table(create_dummy_classes(2))
        self.player_1 = self.table._players
        self.player_2 = self.player_1.next

    def prepare_game(self) -> None:
        self.table._deck.shuffle()
        self.table._deal_cards()
        self.table._collect_blinds()
        self.table._current_raise = self.table._current_bet = self.table._small_bet

    def test_is_round_active_all_in_as_big_blind(self) -> None:
        self.player_2.spend_chips(8)
        self.prepare_game()

        self.table._update_round_active_state()

        expected_is_round_active_before_move = True
        actual_is_round_active_before_move = self.table._is_round_active

        self.assertEqual(expected_is_round_active_before_move, actual_is_round_active_before_move)

        self.table._execute_player_move(self.player_2, Moves.ALL_IN)
        self.table._update_round_active_state()

        expected_is_round_after_move = True
        actual_is_round_active_after_move = self.table._is_round_active

        self.assertEqual(expected_is_round_after_move, actual_is_round_active_after_move)

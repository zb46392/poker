from . import TestGame


class TestBlindCollection(TestGame):
    def test_blind_collection(self) -> None:
        player1_before_blind = self.player_1.get_amount_of_chips()
        player2_before_blind = self.player_2.get_amount_of_chips()
        player3_before_blind = self.player_3.get_amount_of_chips()

        self.table._collect_blinds()

        player1_after_blind = self.player_1.get_amount_of_chips()
        player2_after_blind = self.player_2.get_amount_of_chips()
        player3_after_blind = self.player_3.get_amount_of_chips()

        self.assertEqual(player1_before_blind, player1_after_blind)
        self.assertEqual(player2_before_blind - 1, player2_after_blind)
        self.assertEqual(player3_before_blind - 2, player3_after_blind)

from . import TestGame


class TestInitPlayers(TestGame):
    def test_init_players(self) -> None:
        self.assertEqual('Player_1 (Dummy)', self.player_1.name)
        self.assertEqual(self.player_2, self.player_1.next)

        self.assertEqual('Player_2 (Dummy)', self.player_2.name)
        self.assertEqual(self.player_3, self.player_2.next)

        self.assertEqual('Player_3 (Dummy)', self.player_3.name)
        self.assertEqual(self.player_1, self.player_3.next)

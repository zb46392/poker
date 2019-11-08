from . import TestGame


class TestInitPlayers(TestGame):
    def test_init_players(self):
        self.assertEqual('Player_1', self.table.players[self.player_1]['name'])
        self.assertEqual(self.player_2, self.table.players[self.player_1]['next_player'])

        self.assertEqual('Player_2', self.table.players[self.player_2]['name'])
        self.assertEqual(self.player_3, self.table.players[self.player_2]['next_player'])

        self.assertEqual('Player_3', self.table.players[self.player_3]['name'])
        self.assertEqual(self.player_1, self.table.players[self.player_3]['next_player'])

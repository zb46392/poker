from . import TestGame
from game.deck.card import Card
from game import Table
from . import create_dummy_classes


class TestPotCollection(TestGame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.table = Table(create_dummy_classes(4))
        self.player_1 = self.table.get_dealer()
        self.player_2 = self.table.get_next_player(self.player_1)
        self.player_3 = self.table.get_next_player(self.player_2)
        self.player_4 = self.table.get_next_player(self.player_3)

        self.moves = self.table.Moves

    def prepare_game(self, community_cards, player_1_cards, player_2_cards, player_3_cards, player_4_cards):
        for card in community_cards:
            self.table.community_cards.append(card)

        self.player_1.receive_cards(player_1_cards)
        self.player_2.receive_cards(player_2_cards)
        self.player_3.receive_cards(player_3_cards)
        self.player_4.receive_cards(player_4_cards)

    def test_usual(self):
        self.prepare_game([
            Card('2', 'Heart', 1),
            Card('2', 'Diamond', 1),
            Card('4', 'Spade', 3),
            Card('5', 'Club', 4),
            Card('7', 'Heart', 6)
        ],
            [Card('2', 'Club', 1), Card('5', 'Spade', 4)],
            [Card('2', 'Spade', 1), Card('Jack', 'Club', 10)],
            [Card('7', 'Club', 6), Card('Queen', 'Diamond', 11)],
            [Card('5', 'Heart', 4), Card('Queen', 'Spade', 11)]
        )

        self.table.pot = 100
        self.table.init_showdown_phase()
        self.assertEqual(200, self.player_1.get_amount_of_chips())
        self.assertEqual(100, self.player_2.get_amount_of_chips())
        self.assertEqual(100, self.player_3.get_amount_of_chips())
        self.assertEqual(100, self.player_4.get_amount_of_chips())
        self.assertEqual(0, self.table.pot)

    def test_draw_win_high_card(self):
        """
        Players with same score, pot collects player with high card
        """
        self.prepare_game([
            Card('2', 'Heart', 1),
            Card('King', 'Diamond', 12),
            Card('4', 'Spade', 3),
            Card('5', 'Club', 4),
            Card('7', 'Heart', 6)
        ],
            [Card('King', 'Club', 12), Card('10', 'Spade', 9)],
            [Card('King', 'Spade', 12), Card('Jack', 'Club', 10)],
            [Card('King', 'Heart', 12), Card('Queen', 'Diamond', 11)],
            [Card('Jack', 'Spade', 10), Card('Ace', 'Heart', 13)]
        )

        self.table.players[self.player_1]['current_bet'] = 10
        self.table.players[self.player_1]['total_bet'] = 10

        self.table.players[self.player_2]['current_bet'] = 10
        self.table.players[self.player_2]['total_bet'] = 10

        self.table.players[self.player_3]['current_bet'] = 10
        self.table.players[self.player_3]['total_bet'] = 10

        self.table.players[self.player_4]['current_bet'] = 10
        self.table.players[self.player_4]['total_bet'] = 10

        self.table.pot = 40
        self.table.init_showdown_phase()

        self.assertEqual(100, self.player_1.get_amount_of_chips())
        self.assertEqual(100, self.player_2.get_amount_of_chips())
        self.assertEqual(140, self.player_3.get_amount_of_chips())
        self.assertEqual(100, self.player_4.get_amount_of_chips())

    def test_draw_split_pot_with_leftover(self):
        """
        Multiple players with same score divide pot (with possibility to not be able to split pot equally)
        """

        self.prepare_game([
            Card('10', 'Spade', 9),
            Card('Jack', 'Spade', 10),
            Card('Queen', 'Spade', 11),
            Card('King', 'Spade', 12),
            Card('Ace', 'Spade', 13)
        ],
            [Card('2', 'Club', 1), Card('3', 'Spade', 2)],
            [Card('2', 'Spade', 1), Card('3', 'Club', 2)],
            [Card('2', 'Heart', 1), Card('3', 'Diamond', 2)],
            [Card('2', 'Diamond', 1), Card('3', 'Heart', 2)]
        )

        self.table.players[self.player_1]['current_bet'] = 20
        self.table.players[self.player_1]['total_bet'] = 20

        self.table.players[self.player_2]['current_bet'] = 20
        self.table.players[self.player_2]['total_bet'] = 20

        self.table.players[self.player_3]['current_bet'] = 20
        self.table.players[self.player_3]['total_bet'] = 20

        self.table.players[self.player_4]['current_bet'] = 20
        self.table.players[self.player_4]['total_bet'] = 20
        self.table.players[self.player_4]['current_move'] = self.table.Moves.FOLD

        self.table.pot = 80
        self.table.init_showdown_phase()

        self.assertEqual(126, self.player_1.get_amount_of_chips())
        self.assertEqual(126, self.player_2.get_amount_of_chips())
        self.assertEqual(126, self.player_3.get_amount_of_chips())
        self.assertEqual(100, self.player_4.get_amount_of_chips())
        self.assertEqual(2, self.table.pot_leftover)

    def test_all_in_winner(self):
        """
        At least one player who went all in as winning player: All in player collects part of the pot,
        reminding players divide rest (with possibility to not be able to split pot equally)
        """
        self.prepare_game([
            Card('Ace', 'Heart', 13),
            Card('7', 'Diamond', 6),
            Card('8', 'Diamond', 7),
            Card('9', 'Diamond', 8),
            Card('Queen', 'Heart', 11)
        ],
            [Card('10', 'Diamond', 9), Card('Jack', 'Diamond', 10)],
            [Card('10', 'Spade', 9), Card('Jack', 'Club', 10)],
            [Card('10', 'Club', 9), Card('Jack', 'Diamond', 10)],
            [Card('10', 'Heart', 9), Card('Jack', 'Heart', 10)]
        )

        self.table.players[self.player_1]['current_bet'] = 3
        self.table.players[self.player_1]['total_bet'] = 3
        self.table.players[self.player_1]['current_move'] = self.table.Moves.ALL_IN

        self.table.players[self.player_2]['current_bet'] = 6
        self.table.players[self.player_2]['total_bet'] = 6
        self.table.players[self.player_2]['current_move'] = self.table.Moves.FOLD

        self.table.players[self.player_3]['current_bet'] = 9
        self.table.players[self.player_3]['total_bet'] = 9
        self.table.players[self.player_3]['current_move'] = self.table.Moves.ALL_IN

        self.table.players[self.player_4]['current_bet'] = 9
        self.table.players[self.player_4]['total_bet'] = 9
        self.table.players[self.player_4]['current_move'] = self.table.Moves.ALL_IN

        self.table.pot = 27
        self.table.init_showdown_phase()

        self.assertEqual(112, self.player_1.get_amount_of_chips())
        self.assertEqual(100, self.player_2.get_amount_of_chips())
        self.assertEqual(107, self.player_3.get_amount_of_chips())
        self.assertEqual(107, self.player_4.get_amount_of_chips())
        self.assertEqual(1, self.table.pot_leftover)

    def test_draw_with_all_in(self):
        """
        All players with same score, one went all in
        """

        self.prepare_game([
            Card('3', 'Diamond', 2),
            Card('4', 'Heart', 3),
            Card('5', 'Club', 4),
            Card('6', 'Spade', 5),
            Card('7', 'Diamond', 6)
        ],
            [Card('9', 'Club', 8), Card('9', 'Spade', 8)],
            [Card('10', 'Spade', 9), Card('10', 'Club', 9)],
            [Card('King', 'Heart', 12), Card('Queen', 'Diamond', 11)],
            [Card('Ace', 'Diamond', 13), Card('King', 'Heart', 12)]
        )

        self.table.players[self.player_1]['current_bet'] = 7
        self.table.players[self.player_1]['total_bet'] = 7
        self.table.players[self.player_1]['current_move'] = self.table.Moves.ALL_IN

        self.table.players[self.player_2]['current_bet'] = 15
        self.table.players[self.player_2]['total_bet'] = 15

        self.table.players[self.player_3]['current_bet'] = 15
        self.table.players[self.player_3]['total_bet'] = 15

        self.table.players[self.player_4]['current_bet'] = 15
        self.table.players[self.player_4]['total_bet'] = 15

        self.table.pot = 52
        self.table.init_showdown_phase()

        self.assertEqual(107, self.player_1.get_amount_of_chips())
        self.assertEqual(115, self.player_2.get_amount_of_chips())
        self.assertEqual(115, self.player_3.get_amount_of_chips())
        self.assertEqual(115, self.player_4.get_amount_of_chips())

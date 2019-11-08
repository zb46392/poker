from . import TestGame
from game.deck.card import Card


class TestFindStrongestFinalHand(TestGame):
    def prepare_game(self, community_cards, player_1_cards, player_2_cards, player_3_cards):
        for card in community_cards:
            self.table.community_cards.append(card)

        self.player_1.receive_cards(player_1_cards)
        self.player_2.receive_cards(player_2_cards)
        self.player_3.receive_cards(player_3_cards)

    def test_high_card(self):
        self.prepare_game([
            Card('2', 'Heart', 1),
            Card('3', 'Diamond', 2),
            Card('4', 'Spade', 3),
            Card('6', 'Club', 5),
            Card('7', 'Heart', 6)
        ],
            [Card('8', 'Diamond', 7), Card('9', 'Spade', 8)],
            [Card('10', 'Heart', 9), Card('Jack', 'Club', 10)],
            [Card('Ace', 'Club', 13), Card('Queen', 'Diamond', 11)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.HIGH_CARD,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(8, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.HIGH_CARD,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(10, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.HIGH_CARD,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(13, self.table.players[self.player_3]['score'])

    def test_pair(self):
        self.prepare_game([
            Card('2', 'Heart', 1),
            Card('Ace', 'Diamond', 13),
            Card('3', 'Diamond', 2),
            Card('5', 'Club', 4),
            Card('9', 'Heart', 8),
        ],
            [Card('2', 'Spade', 1), Card('King', 'Spade', 12)],
            [Card('Ace', 'Club', 13), Card('7', 'Heart', 6)],
            [Card('Queen', 'Diamond', 11), Card('Queen', 'Spade', 11)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.PAIR,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(20, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.PAIR,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(260, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.PAIR,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(220, self.table.players[self.player_3]['score'])

    def test_two_pairs(self):
        self.prepare_game([
            Card('2', 'Diamond', 1),
            Card('3', 'Spade', 2),
            Card('3', 'Club', 2),
            Card('King', 'Heart', 12),
            Card('Ace', 'Diamond', 13),
        ],
            [Card('2', 'Spade', 1), Card('6', 'Club', 5)],
            [Card('6', 'Heart', 5), Card('6', 'Diamond', 5)],
            [Card('Ace', 'Spade', 13), Card('King', 'Club', 12)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.TWO_PAIRS,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(601, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.TWO_PAIRS,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(1502, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.TWO_PAIRS,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(3912, self.table.players[self.player_3]['score'])

    def tris(self):
        self.prepare_game([
            Card('King', 'Club', 13),
            Card('2', 'Club', 1),
            Card('8', 'Heart', 7),
            Card('Ace', 'Diamond', 13),
            Card('10', 'Spade', 9),
        ],
            [Card('2', 'Heart', 1), Card('2', 'Spade', 1)],
            [Card('8', 'Diamond', 7), Card('8', 'Club', 7)],
            [Card('Ace', 'Heart', 13), Card('Ace', 'Spade', 13)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.TRIS,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(4000, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.TRIS,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(32000, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.TRIS,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(52000, self.table.players[self.player_3]['score'])

    def test_straight(self):
        self.prepare_game([
            Card('2', 'Club', 1),
            Card('4', 'Heart', 3),
            Card('5', 'Diamond', 4),
            Card('7', 'Heart', 6),
            Card('8', 'Club', 7),
        ],
            [Card('Ace', 'Heart', 13), Card('3', 'Spade', 2)],
            [Card('3', 'Diamond', 2), Card('6', 'Club', 5)],
            [Card('6', 'Spade', 5), Card('9', 'Diamond', 8)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(60000, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(105000, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(120000, self.table.players[self.player_3]['score'])

        self.reset()
        self.prepare_game([
            Card('Queen', 'Spade', 11),
            Card('Jack', 'Club', 10),
            Card('10', 'Heart', 9),
            Card('8', 'Diamond', 7),
            Card('8', 'Spade', 7),
        ],
            [Card('Ace', 'Club', 13), Card('King', 'Heart', 12)],
            [Card('King', 'Diamond', 12), Card('9', 'Spade', 8)],
            [Card('9', 'Club', 8), Card('8', 'Heart', 7)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(195000, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(180000, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(165000, self.table.players[self.player_3]['score'])

    def test_flush(self):
        self.prepare_game([
            Card('3', 'Club', 2),
            Card('Queen', 'Diamond', 11),
            Card('Jack', 'Diamond', 10),
            Card('9', 'Diamond', 8),
            Card('8', 'Heart', 7),
        ],
            [Card('Ace', 'Diamond', 13), Card('10', 'Diamond', 9)],
            [Card('King', 'Diamond', 12), Card('2', 'Diamond', 1)],
            [Card('8', 'Diamond', 7), Card('7', 'Diamond', 6)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.FLUSH,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(429000, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FLUSH,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(396000, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FLUSH,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(363000, self.table.players[self.player_3]['score'])

        self.reset()
        self.prepare_game([
            Card('4', 'Club', 3),
            Card('5', 'Club', 4),
            Card('7', 'Club', 6),
            Card('6', 'Spade', 5),
            Card('8', 'Spade', 7),
        ],
            [Card('2', 'Club', 1), Card('3', 'Club', 2)],
            [Card('9', 'Club', 8), Card('8', 'Club', 7)],
            [Card('6', 'Club', 5), Card('10', 'Club', 9)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.FLUSH,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(198000, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FLUSH,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(264000, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FLUSH,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(297000, self.table.players[self.player_3]['score'])

    def test_full_house(self):
        self.prepare_game([
            Card('Ace', 'Heart', 13),
            Card('2', 'Diamond', 1),
            Card('2', 'Spade', 1),
            Card('3', 'Club', 2),
            Card('3', 'Heart', 2),
        ],
            [Card('King', 'Diamond', 12), Card('2', 'Club', 1)],
            [Card('3', 'Diamond', 2), Card('2', 'Heart', 1)],
            [Card('3', 'Spade', 2), Card('King', 'Spade', 12)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.FULL_HOUSE,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(500002, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FULL_HOUSE,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(1000001, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FULL_HOUSE,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(1000001, self.table.players[self.player_3]['score'])

        self.reset()
        self.prepare_game([
            Card('2', 'Club', 1),
            Card('Ace', 'Heart', 13),
            Card('King', 'Diamond', 12),
            Card('King', 'Spade', 12),
            Card('3', 'Club', 2),
        ],
            [Card('Ace', 'Diamond', 13), Card('Ace', 'Spade', 13)],
            [Card('Ace', 'Club', 13), Card('King', 'Club', 12)],
            [Card('King', 'Heart', 12), Card('3', 'Heart', 2)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.FULL_HOUSE,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(6500012, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FULL_HOUSE,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(6000013, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FULL_HOUSE,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(6000002, self.table.players[self.player_3]['score'])

    def test_poker(self):
        self.prepare_game([
            Card('2', 'Spade', 1),
            Card('2', 'Club', 1),
            Card('Ace', 'Heart', 13),
            Card('Ace', 'Diamond', 13),
            Card('King', 'Spade', 12),
        ],
            [Card('2', 'Heart', 1), Card('2', 'Heart', 1)],
            [Card('Ace', 'Club', 13), Card('Ace', 'Spade', 13)],
            [Card('King', 'Club', 12), Card('King', 'Heart', 12)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.POKER,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(6600000, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.POKER,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(85800000, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.FULL_HOUSE,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(6000013, self.table.players[self.player_3]['score'])

    def test_straight_flush(self):
        self.prepare_game([
            Card('3', 'Heart', 2),
            Card('4', 'Heart', 3),
            Card('5', 'Heart', 4),
            Card('6', 'Spade', 5),
            Card('8', 'Club', 7),
        ],
            [Card('Ace', 'Heart', 13), Card('2', 'Heart', 1)],
            [Card('7', 'Spade', 6), Card('9', 'Diamond', 8)],
            [Card('6', 'Heart', 5), Card('7', 'Heart', 6)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT_FLUSH,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(86000000, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(120000, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT_FLUSH,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(129000000, self.table.players[self.player_3]['score'])

        self.reset()
        self.prepare_game([
            Card('Queen', 'Club', 11),
            Card('Jack', 'Club', 10),
            Card('10', 'Club', 9),
            Card('8', 'Diamond', 7),
            Card('8', 'Spade', 7),
        ],
            [Card('Ace', 'Club', 13), Card('King', 'Club', 12)],
            [Card('9', 'Diamond', 8), Card('8', 'Heart', 7)],
            [Card('9', 'Club', 8), Card('8', 'Club', 7)]
        )

        self.table.find_players_final_hand()

        self.assertEqual(self.table.FinalHandMultipliers.ROYAL_FLUSH,
                         self.table.players[self.player_1]['final_hand_type'])
        self.assertEqual(286000000, self.table.players[self.player_1]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT,
                         self.table.players[self.player_2]['final_hand_type'])
        self.assertEqual(165000, self.table.players[self.player_2]['score'])

        self.assertEqual(self.table.FinalHandMultipliers.STRAIGHT_FLUSH,
                         self.table.players[self.player_3]['final_hand_type'])
        self.assertEqual(236500000, self.table.players[self.player_3]['score'])

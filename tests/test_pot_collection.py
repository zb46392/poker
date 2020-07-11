from . import TestGame
from .dummy_player import create_dummy_classes
from game import Card, Moves, Table
from typing import List


class TestPotCollection(TestGame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.table = Table(create_dummy_classes(4))
        self.player_1 = self.table._players
        self.player_2 = self.player_1.next
        self.player_3 = self.player_2.next
        self.player_4 = self.player_3.next

        self.moves = Moves

    def prepare_game(self, community_cards: List[Card],
                     player_1_cards: List[Card], player_2_cards: List[Card],
                     player_3_cards: List[Card], player_4_cards: List[Card]) -> None:
        for card in community_cards:
            self.table._community_cards.append(card)

        self.player_1.receive_cards(player_1_cards)
        self.player_2.receive_cards(player_2_cards)
        self.player_3.receive_cards(player_3_cards)
        self.player_4.receive_cards(player_4_cards)

    def test_usual(self) -> None:
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

        self.table._pot = 100

        self.player_1.total_bet = 25
        self.player_2.total_bet = 25
        self.player_3.total_bet = 25
        self.player_4.total_bet = 25

        self.table.init_showdown_phase()
        self.assertEqual(200, self.player_1.get_amount_of_chips())
        self.assertEqual(100, self.player_2.get_amount_of_chips())
        self.assertEqual(100, self.player_3.get_amount_of_chips())
        self.assertEqual(100, self.player_4.get_amount_of_chips())
        self.assertEqual(0, self.table._pot)

    def test_draw_win_high_card(self) -> None:
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

        self.player_1.current_bet = 10
        self.player_1.total_bet = 10

        self.player_2.current_bet = 10
        self.player_2.total_bet = 10

        self.player_3.current_bet = 10
        self.player_3.total_bet = 10

        self.player_4.current_bet = 10
        self.player_4.total_bet = 10

        self.table._pot = 40
        self.table.init_showdown_phase()

        self.assertEqual(100, self.player_1.get_amount_of_chips())
        self.assertEqual(100, self.player_2.get_amount_of_chips())
        self.assertEqual(140, self.player_3.get_amount_of_chips())
        self.assertEqual(100, self.player_4.get_amount_of_chips())

    def test_draw_split_pot_with_leftover(self) -> None:
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

        self.player_1.current_bet = 20
        self.player_1.total_bet = 20

        self.player_2.current_bet = 20
        self.player_2.total_bet = 20

        self.player_3.current_bet = 20
        self.player_3.total_bet = 20

        self.player_4.current_bet = 20
        self.player_4.total_bet = 20
        self.player_4.current_move = self.moves.FOLD

        self.table._pot = 80
        self.table.init_showdown_phase()

        self.assertEqual(126, self.player_1.get_amount_of_chips())
        self.assertEqual(126, self.player_2.get_amount_of_chips())
        self.assertEqual(126, self.player_3.get_amount_of_chips())
        self.assertEqual(100, self.player_4.get_amount_of_chips())
        self.assertEqual(2, self.table._pot_leftover)

    def test_all_in_winner(self) -> None:
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

        self.player_1.current_bet = 3
        self.player_1.total_bet = 3
        self.player_1.current_move = self.moves.ALL_IN

        self.player_2.current_bet = 6
        self.player_2.total_bet = 6
        self.player_2.current_move = self.moves.FOLD

        self.player_3.current_bet = 9
        self.player_3.total_bet = 9
        self.player_3.current_move = self.moves.ALL_IN

        self.player_4.current_bet = 9
        self.player_4.total_bet = 9
        self.player_4.current_move = self.moves.ALL_IN

        self.table._pot = 27
        self.table.init_showdown_phase()

        self.assertEqual(112, self.player_1.get_amount_of_chips())
        self.assertEqual(100, self.player_2.get_amount_of_chips())
        self.assertEqual(107, self.player_3.get_amount_of_chips())
        self.assertEqual(107, self.player_4.get_amount_of_chips())
        self.assertEqual(1, self.table._pot_leftover)

    def test_draw_with_all_in(self) -> None:
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

        self.player_1.current_bet = 7
        self.player_1.total_bet = 7
        self.player_1.current_move = self.moves.ALL_IN

        self.player_2.current_bet = 15
        self.player_2.total_bet = 15

        self.player_3.current_bet = 15
        self.player_3.total_bet = 15

        self.player_4.current_bet = 15
        self.player_4.total_bet = 15

        self.table._pot = 52
        self.table.init_showdown_phase()

        self.assertEqual(107, self.player_1.get_amount_of_chips())
        self.assertEqual(115, self.player_2.get_amount_of_chips())
        self.assertEqual(115, self.player_3.get_amount_of_chips())
        self.assertEqual(115, self.player_4.get_amount_of_chips())

    def test_bug_case_00(self) -> None:
        """
        Situation:
         - All in player is winner
         - Next best player collects rest

         Total pot = 28
         All in player received:    24 :: (24)
         Next best player received: 28 :: (4)
        """
        table = Table(create_dummy_classes(3))

        player_1 = table._players
        player_2 = table._players.next
        player_3 = table._players.next.next

        table._community_cards = [
            Card('9', 'Heart', 8),
            Card('Jack', 'Spade', 10),
            Card('5', 'Heart', 4),
            Card('Ace', 'Diamond', 13),
            Card('10', 'Diamond', 9)
        ]

        player_1._basic_player._hand = [Card('2', 'Spade', 1), Card('Queen', 'Spade', 11)]
        player_2._basic_player._hand = [Card('King', 'Spade', 12), Card('King', 'Diamond', 12)]
        player_3._basic_player._hand = [Card('8', 'Spade', 7), Card('6', 'Spade', 5)]

        table._pot = 28

        player_1.total_bet = 10
        player_1.current_move = Moves.CHECK
        player_1._basic_player._chips = 71

        player_2.total_bet = 8
        player_2.current_move = Moves.ALL_IN
        player_2._basic_player._chips = 0

        player_3.total_bet = 10
        player_3.current_move = Moves.CHECK
        player_3._basic_player._chips = 51

        table.init_showdown_phase()

        self.assertEqual(75, player_1.get_amount_of_chips())
        self.assertEqual(24, player_2.get_amount_of_chips())
        self.assertEqual(51, player_3.get_amount_of_chips())

    def test_bug_case_01(self) -> None:
        """
        Situation:
        4 players. All in player & another not all in player split the pot.

        Total pot: 14
        All in player received:     5 : (4)
        Not all in player received: 9 : (10)
        """
        #
        table = Table(create_dummy_classes(4))
        table.INIT_CHIPS = 100

        player_1 = table._players
        player_2 = player_1.next
        player_3 = player_2.next
        player_4 = player_3.next

        table._community_cards = [
            Card('Queen', 'Spade', 11),
            Card('10', 'Club', 9),
            Card('Jack', 'Spade', 10),
            Card('Jack', 'Diamond', 10),
            Card('8', 'Spade', 7)
        ]

        player_1.receive_cards([Card('Jack', 'Heart', 10), Card('8', 'Diamond', 7)])
        player_2.receive_cards([Card('4', 'Club', 3), Card('Queen', 'Club', 11)])
        player_3.receive_cards([Card('6', 'Diamond', 5), Card('Ace', 'Spade', 13)])
        player_4.receive_cards([Card('2', 'Heart', 1), Card('Queen', 'Diamond', 11)])

        table._pot = 14

        player_1.total_bet = 4
        player_1.current_move = Moves.FOLD
        player_1._basic_player._chips = 38

        player_2.total_bet = 6
        player_2.current_move = Moves.RAISE
        player_2._basic_player._chips = 164

        player_3.total_bet = 2
        player_3.current_move = Moves.FOLD
        player_3._basic_player._chips = 34

        player_4.total_bet = 2
        player_4.current_move = Moves.ALL_IN
        player_4._basic_player._chips = 0

        table.init_showdown_phase()

        self.assertEqual(38, player_1.get_amount_of_chips())
        self.assertEqual(174, player_2.get_amount_of_chips())
        self.assertEqual(34, player_3.get_amount_of_chips())
        self.assertEqual(4, player_4.get_amount_of_chips())

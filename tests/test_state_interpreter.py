from game import State, Card, Phases, Moves, Dummy
from game.player.dqn.state_interpreter import StateInterpreterV1, StateInterpreterV2, InterpretableState
import unittest
from unittest import TestCase


class TestStateInterpreterV1(TestCase):

    def test_state_interpretation(self) -> None:
        player = Dummy(10)
        player.receive_cards([Card('7', 'Spade', 6), Card('10', 'Diamond', 9)])
        state = State(
            community_cards=(Card('10', 'Spade', 9), Card('6', 'Diamond', 5), Card('4', 'Club', 3),
                             Card('2', 'Spade', 1), Card('Queen', 'Diamond', 11)),
            total_players=3,
            total_chips=30,
            nbr_of_active_players=3,
            current_phase=Phases.RIVER,
            is_raising_capped=False,
            allowed_moves=(Moves.CHECK, Moves.FOLD, Moves.RAISE),
            pot=3,
            current_bet=2
        )

        player.spend_chips(4)

        inter = StateInterpreterV1()
        interpretable_state = InterpretableState(
            game_state=state,
            hand=tuple(player.get_hand()),
            current_chips_amount=player.get_amount_of_chips()
        )

        #           H   D   S   C
        expected = [0., 0., 1., 0.,  # 2
                    0., 0., 0., 0.,  # 3
                    0., 0., 0., 1.,  # 4
                    0., 0., 0., 0.,  # 5
                    0., 1., 0., 0.,  # 6
                    0., 0., 1., 0.,  # 7
                    0., 0., 0., 0.,  # 8
                    0., 0., 0., 0.,  # 9
                    0., 1., 1., 0.,  # 10
                    0., 0., 0., 0.,  # Jack
                    0., 1., 0., 0.,  # Queen
                    0., 0., 0., 0.,  # King
                    0., 0., 0., 0.,  # Ace
                    # CHIPS
                    0., 0., 0., 0.,
                    0., 0., 0., 0.,
                    0., 0., 0., 0.,
                    0., 0., 0., 0.,
                    0., 0., 0., 0.,
                    0., 0., 0., 0.,
                    1., 1., 1., 1.,
                    1., 1.,
                    # is raising capped
                    0.,
                    ]
        actual = inter.interpret(interpretable_state)

        self.assertEqual(expected, actual)


class TestStateInterpreterV2(TestCase):

    def test_state_interpretation(self) -> None:
        player = Dummy(10)
        player.receive_cards([Card('7', 'Spade', 6), Card('10', 'Diamond', 9)])
        state = State(
            community_cards=(Card('10', 'Spade', 9), Card('6', 'Diamond', 5), Card('4', 'Club', 3),
                             Card('2', 'Spade', 1), Card('Queen', 'Diamond', 11)),
            total_players=3,
            total_chips=30,
            nbr_of_active_players=3,
            current_phase=Phases.RIVER,
            is_raising_capped=False,
            allowed_moves=(Moves.CALL, Moves.FOLD, Moves.RAISE),
            pot=3,
            current_bet=2
        )

        inter = StateInterpreterV2()
        interpretable_state = InterpretableState(
            game_state=state,
            hand=tuple(player.get_hand()),
            current_chips_amount=player.get_amount_of_chips()
        )

        #           HAND
        #           H   D   S   C
        expected = [0., 0., 0., 0.,  # 2
                    0., 0., 0., 0.,  # 3
                    0., 0., 0., 0.,  # 4
                    0., 0., 0., 0.,  # 5
                    0., 0., 0., 0.,  # 6
                    0., 0., 1., 0.,  # 7
                    0., 0., 0., 0.,  # 8
                    0., 0., 0., 0.,  # 9
                    0., 1., 0., 0.,  # 10
                    0., 0., 0., 0.,  # Jack
                    0., 0., 0., 0.,  # Queen
                    0., 0., 0., 0.,  # King
                    0., 0., 0., 0.,  # Ace
                    # COMMUNITY
                    0., 0., 1., 0.,  # 2
                    0., 0., 0., 0.,  # 3
                    0., 0., 0., 1.,  # 4
                    0., 0., 0., 0.,  # 5
                    0., 1., 0., 0.,  # 6
                    0., 0., 0., 0.,  # 7
                    0., 0., 0., 0.,  # 8
                    0., 0., 0., 0.,  # 9
                    0., 0., 1., 0.,  # 10
                    0., 0., 0., 0.,  # Jack
                    0., 1., 0., 0.,  # Queen
                    0., 0., 0., 0.,  # King
                    0., 0., 0., 0.,  # Ace
                    # HAND TYPE
                    0., 1., 0., 0., 0.,
                    0., 0., 0., 0., 0.,

                    # ALLOWED MOVES
                    1., 0., 1., 1., 0.
                    ]
        actual = inter.interpret(interpretable_state)

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

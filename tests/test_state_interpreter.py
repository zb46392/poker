from game import State, Card, Phases
from game.player.dqn.state_interpreter import StateInterpreter
import unittest
from unittest import TestCase


class TestStateInterpreter(TestCase):

    def test_state_interpretation(self) -> None:
        hand = [Card('7', 'Spade', 6), Card('10', 'Diamond', 9)]
        s = State(
            community_cards=[Card('10', 'Spade', 9), Card('6', 'Diamond', 5), Card('4', 'Club', 3),
                             Card('2', 'Spade', 1), Card('Queen', 'Diamond', 11)],
            total_nbr_of_players=3,
            nbr_of_active_players=3,
            current_phase=Phases.RIVER,
            is_raising_capped=False
        )
        inter = StateInterpreter(10)
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
        actual = inter.interpret(hand, s, 6)

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

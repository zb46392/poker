from game import Player, Moves, State
from typing import List


class TerminalPlayer(Player):
    def make_move(self, possible_moves: List[Moves], game_state: State) -> Moves:
        choice = None

        while choice not in range(len(possible_moves)):
            print('********* MAKE A MOVE! *********')
            for i, move in enumerate(possible_moves):
                print(f'{i}: {move}')

            try:
                choice = int(input("Enter your choice: "))
            except Exception as e:
                choice = None
        print('************************************')
        return possible_moves[choice]

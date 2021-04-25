from . import Player
from game import Moves, State
from typing import List, Optional
import os


class TerminalPlayer(Player):
    def __init__(self, chips: int, name: Optional[str] = None) -> None:
        super().__init__(chips, name)
        self._previous_chips = self._chips
        self._current_phase = None
        self._current_bet = 0

    def make_move(self, possible_moves: List[Moves], game_state: State) -> Moves:
        choice = None

        if self._current_phase is not game_state.current_phase:
            self._current_bet = 0
            self._current_phase = game_state.current_phase

        current_phase = str(game_state.current_phase)
        pot = str(game_state.pot)
        current_bet = str(game_state.current_bet)
        community_cards = str(game_state.community_cards)[1:-1]
        hand = str(self.get_hand())[1:-1]
        chips = str(self.get_amount_of_chips())
        wager = str(self.wager)
        to_call = str(game_state.current_bet - self._current_bet)

        while choice not in range(len(possible_moves)):
            self.clear()
            print()
            print(
                '+------------------------------------------ CURRENT  STATE ------------------------------------------+')
            print(f'|{str():100}|')
            print(f'|  Phase: {current_phase:91}|')
            print(f'|  Pot: {pot:93}|')
            print(f'|  Current bet: {current_bet:85}|')
            print(f'|  Community cards: {community_cards:81}|')
            print(f'|  Hand: {hand:92}|')
            print(f'|  Chips: {chips:91}|')
            print(f'|  Wager: {wager:91}|')
            if Moves.CALL in possible_moves:
                print(f'|  To call: {to_call:89}|')
            print(f'|{str():100}|')
            print(f'|  Allowed moves: {str():83}|')
            for i, move in enumerate(possible_moves):
                print(f'|   [ {i} ]: {move:90}|')
            print(f'|{str():100}|')
            print(
                '+----------------------------------------------------------------------------------------------------+')
            try:
                choice = int(input('Enter your choice: '))
            except Exception as e:
                choice = None

        return possible_moves[choice]

    @staticmethod
    def clear() -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def spend_chips(self, amount: int) -> int:
        self._current_bet += amount
        return super().spend_chips(amount)

    def receive_chips(self, amount: int):
        super().receive_chips(amount)
        print()
        if amount > 0:
            print(f'You won {amount} chips.')
        else:
            print(f'You lost {self._previous_chips - self._chips} chips.')

        self._previous_chips = self._chips
        self._current_bet = 0

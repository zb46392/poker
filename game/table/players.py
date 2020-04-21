from copy import deepcopy
from game import Card, FinalHandType, Moves, Player as Basic_Player, State
from typing import List, Optional


class Players:
    def __init__(self, basic_player: Basic_Player, name: str = 'Player') -> None:
        self._basic_player = basic_player
        self._name = name
        self._current_bet = 0
        self._total_bet = 0
        self._score = 0
        self._current_move = None
        self._final_hand = None
        self._final_hand_type = None
        self._next = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def current_bet(self) -> int:
        return self._current_bet

    @current_bet.setter
    def current_bet(self, bet: int) -> None:
        self._current_bet = bet

    @property
    def total_bet(self) -> int:
        return self._total_bet

    @total_bet.setter
    def total_bet(self, bet: int) -> None:
        self._total_bet = bet

    @property
    def current_move(self) -> Moves:
        return self._current_move

    @current_move.setter
    def current_move(self, move: Moves) -> None:
        self._current_move = move

    @property
    def final_hand(self) -> List[Card]:
        return self._final_hand

    @final_hand.setter
    def final_hand(self, hand: List[Card]) -> None:
        self._final_hand = hand

    @property
    def final_hand_type(self) -> FinalHandType:
        return self._final_hand_type

    @final_hand_type.setter
    def final_hand_type(self, hand_type: FinalHandType) -> None:
        self._final_hand_type = hand_type

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, score: int) -> None:
        self._score = score

    @property
    def next(self) -> 'Players':
        return self._next

    @next.setter
    def next(self, player: 'Players') -> None:
        self._next = player

    def receive_cards(self, cards: List[Card]) -> None:
        self._basic_player.receive_cards(cards)

    def get_amount_of_chips(self) -> int:
        return self._basic_player.get_amount_of_chips()

    def spend_chips(self, amount: int) -> int:
        return self._basic_player.spend_chips(amount)

    def make_move(self, possible_moves: List[Moves], game_state: State) -> Moves:
        return self._basic_player.make_move(possible_moves, game_state)

    def get_hand(self) -> List[Card]:
        return self._basic_player.get_hand()

    def receive_chips(self, amount: int) -> None:
        self._basic_player.receive_chips(amount)

    def destroy_hand(self) -> None:
        self._basic_player.destroy_hand()

    def reset(self):
        self._basic_player.destroy_hand()
        self._current_move = None
        self._current_bet = 0
        self._total_bet = 0
        self._final_hand = None
        self._final_hand_type = None
        self._score = 0

    def append(self, player: 'Players') -> None:
        tmp = self
        is_closed_list = False

        while tmp.next is not None:
            if tmp.next == self:
                is_closed_list = True
                tmp.next = None
            else:
                tmp = tmp.next

        tmp.next = player

        if is_closed_list:
            player.next = self

    def get_by_position(self, position: int = 1) -> 'Players':
        next_player = self

        for _ in range(position):
            next_player = next_player.next

        return next_player

    def find(self, player_to_find: 'Players') -> Optional['Players']:
        if player_to_find == self:
            return player_to_find

        player = self._next

        while player != player_to_find:
            if player == self or player is None:
                return None

            player = player.next

        return player

    def count(self) -> int:
        player = self._next
        cnt = 1

        while player != self and player is not None:
            cnt += 1
            player = player.next

        return cnt

    def clone(self) -> 'Players':
        return deepcopy(self)

    def __iter__(self) -> 'Players':
        self._tmp = self
        self._has_head_been_returned = False
        return self

    def __next__(self) -> 'Players':
        if self._tmp is not None:
            if self._tmp == self:
                if not self._has_head_been_returned:
                    self._has_head_been_returned = True
                else:
                    raise StopIteration

            tmp = self._tmp
            self._tmp = self._tmp.next

            return tmp
        else:
            raise StopIteration

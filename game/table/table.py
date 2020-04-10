from .observer import State as ObserverState, BaseObserver
from .observers import Observers
from .players import Players as TablePlayers
from copy import deepcopy
from game import Deck, Moves, Player as BasicPlayer, State, StrongestFinalHandFinder
from typing import Dict, List, Optional, Type


class Table:
    INIT_CHIPS = 100
    SMALL_BET = 2
    BIG_BET = 4

    def __init__(self, players_classes: List[Type[BasicPlayer]]) -> None:

        self._deck = Deck()
        self._players = self._create_players(players_classes)
        self._pot = 0
        self._pot_leftover = 0
        self._community_cards = []
        self._current_bet = 0
        self._small_bet = self.SMALL_BET
        self._big_bet = self.BIG_BET
        self._current_raise = self._small_bet
        self._raise_cnt = 0
        self._is_game_active = True
        self._observers = Observers()

    def _create_players(self, players_classes: List[Type[BasicPlayer]]) -> TablePlayers:
        if len(players_classes) < 2 or len(players_classes) > 10:
            raise ValueError('Only between 2 and 10 players allowed...')

        dealer = None
        previous_table_player = None

        for player_cnt in range(len(players_classes)):
            basic_player = players_classes[player_cnt](self.INIT_CHIPS)

            if not isinstance(basic_player, BasicPlayer):
                raise ValueError('Class has to be extended from game.Player base class')

            table_player = TablePlayers(basic_player, 'Player_' + str(player_cnt + 1))

            if previous_table_player is not None:
                previous_table_player.next = table_player
            else:
                dealer = table_player

            previous_table_player = table_player

        previous_table_player.next = dealer

        return dealer

    def init_pre_flop_phase(self) -> None:
        self._deck.shuffle()
        self.deal_cards()
        self.collect_blinds()
        self._current_raise = self._current_bet = self._small_bet

        self.init_betting_round(self._players.get_by_position(3))
        self._pot += self.take_from_pot_leftover(self._pot_leftover)

        self.update_game_active_state()
        self.notify_observers(ObserverState(players=self._players.clone(),
                                            community_cards=deepcopy(self._community_cards),
                                            phase='PRE FLOP',
                                            pot=self._pot
                                            ))

    def init_flop_phase(self) -> None:
        if self._is_game_active:
            self.init_common_phase(self._small_bet, cards_to_deal=3)

        self.notify_observers(ObserverState(players=self._players.clone(),
                                            community_cards=deepcopy(self._community_cards),
                                            phase='FLOP',
                                            pot=self._pot
                                            ))

    def init_turn_phase(self) -> None:
        if self._is_game_active:
            self.init_common_phase(self._big_bet)

        self.notify_observers(ObserverState(players=self._players.clone(),
                                            community_cards=deepcopy(self._community_cards),
                                            phase='TURN',
                                            pot=self._pot
                                            ))

    def init_river_phase(self) -> None:
        if self._is_game_active:
            self.init_common_phase(self._big_bet)

        self.notify_observers(ObserverState(players=self._players.clone(),
                                            community_cards=deepcopy(self._community_cards),
                                            phase='RIVER',
                                            pot=self._pot
                                            ))

    def init_showdown_phase(self) -> None:
        self.find_players_final_hand()
        self.init_pot_collection()

        self.notify_observers(ObserverState(players=self._players.clone(),
                                            community_cards=deepcopy(self._community_cards),
                                            phase='SHOWDOWN',
                                            pot=self._pot
                                            ))

    def deal_cards(self) -> None:
        for _ in range(2):
            self.deal_one_round()

    def deal_one_round(self) -> None:
        for player in self._players:
            player.basic_player.receive_cards(self._deck.deal())

    def collect_blinds(self) -> None:
        player = self._players.next
        self.collect_blind(player, int(self._small_bet / 2))

        player = player.next
        self.collect_blind(player, self._small_bet)

        self._current_bet = self._small_bet

    def collect_blind(self, player: TablePlayers, blind: int) -> None:
        if player.basic_player.get_amount_of_chips() > blind:
            self.collect_bet(player, blind)
            player.current_bet = blind
        else:
            amount = player.basic_player.get_amount_of_chips()
            self.collect_bet(player, amount)
            player.current_bet = amount
            player.current_move = Moves.ALL_IN

    def collect_bet(self, player: TablePlayers, amount: int) -> None:
        self._pot += player.basic_player.spend_chips(amount)

    def init_betting_round(self, stopping_player: TablePlayers) -> None:
        player = stopping_player

        while True:
            if self.have_all_folded_but_one():
                self._is_game_active = False
                break

            moves = self.generate_player_moves(player)

            if moves is None:
                player = player.next
                if player is stopping_player:
                    break
                continue

            move = player.basic_player.make_move(moves, self.generate_game_state())

            self.execute_player_move(player, move)
            if player.current_bet > self._current_bet:
                stopping_player = player
                self._current_bet = player.current_bet

            player = player.next

            if player is stopping_player:
                break

    def have_all_folded_but_one(self) -> bool:
        if self.count_folded_players() == (self._players.count() - 1):
            return True
        else:
            return False

    def count_folded_players(self) -> int:
        folded_players = 0

        for player in self._players:
            if player.current_move is Moves.FOLD:
                folded_players += 1

        return folded_players

    def generate_player_moves(self, player: TablePlayers) -> Optional[List[Moves]]:
        moves = list()

        if player.current_move is Moves.FOLD or player.current_move is Moves.ALL_IN:
            return None

        if player.current_bet < self._current_bet < player.basic_player.get_amount_of_chips():
            moves.append(Moves.CALL)

        if player.basic_player.get_amount_of_chips() <= self._current_bet \
                or (player.basic_player.get_amount_of_chips() <= (self._current_bet + self._current_raise)
                    and not self.is_raising_capped()):
            moves.append(Moves.ALL_IN)

        if self._current_bet == player.current_bet:
            moves.append(Moves.CHECK)

        if not self.is_raising_capped() \
                and player.basic_player.get_amount_of_chips() > (self._current_bet + self._current_raise):
            moves.append(Moves.RAISE)

        moves.append(Moves.FOLD)

        return moves

    def is_raising_capped(self) -> bool:
        return not self._raise_cnt < 4

    def generate_game_state(self) -> State:
        return State()

    def execute_player_move(self, player: TablePlayers, move: Moves) -> None:

        if move is Moves.CALL:
            amount = self.calculate_amount_to_call(player)
            self.collect_bet(player, amount)
            player.current_bet += amount
            player.total_bet += amount

        elif move is Moves.RAISE:
            amount = self.calculate_amount_to_raise(player)
            self.collect_bet(player, amount)
            player.current_bet += amount
            player.total_bet += amount
            self._current_bet += self._current_raise
            self._raise_cnt += 1

        elif move is Moves.ALL_IN:
            amount = player.basic_player.get_amount_of_chips()
            self.collect_bet(player, amount)
            player.current_bet += amount
            player.total_bet += amount

        player.current_move = move

    def calculate_amount_to_call(self, player: TablePlayers) -> int:
        return self._current_bet - player.current_bet

    def calculate_amount_to_raise(self, player: TablePlayers) -> int:
        return self.calculate_amount_to_call(player) + self._current_raise

    def update_game_active_state(self) -> None:
        if self.have_all_folded_but_one():
            self._is_game_active = False

    def init_common_phase(self, bet_size: int, cards_to_deal: int = 1) -> None:
        self.prepare_common_phase(bet_size)

        self._deck.burn()
        self._community_cards += self._deck.deal(cards_to_deal)
        self.init_betting_round(self._players.next)

        self.update_game_active_state()

    def prepare_common_phase(self, bet_amount: int) -> None:
        self._current_raise = bet_amount
        self._raise_cnt = 0
        self._current_bet = 0

    def find_players_final_hand(self) -> None:

        for player in self._players:
            if player.current_move is not Moves.FOLD:
                final_hand = StrongestFinalHandFinder.find(self._community_cards + player.basic_player.get_hand())

                player.final_hand = final_hand.hand
                player.final_hand_type = final_hand.type
                player.score = final_hand.score

    def init_pot_collection(self) -> None:
        sorted_players = self.sort_players_by_score()
        individual_pot_collection = self.split_pot_among_players(sorted_players)

        for player in individual_pot_collection:
            player.basic_player.receive_chips(self.take_from_pot(individual_pot_collection[player]))

        self._pot_leftover += self.take_from_pot(self._pot)

    def sort_players_by_score(self) -> List[List[TablePlayers]]:
        sorted_players = list()

        for player in self._players:
            sorted_players = self.insert_player_in_sorted_list(player, sorted_players)

        return sorted_players

    def insert_player_in_sorted_list(self, player: TablePlayers, sorted_players: List[List[TablePlayers]]) \
            -> List[List[TablePlayers]]:
        has_player_been_inserted = False

        for i in range(len(sorted_players)):
            if player.score > self._players.find(sorted_players[i][0]).score:
                sorted_players.insert(i, [player])
                has_player_been_inserted = True

            elif player.score == self._players.find(sorted_players[i][0]).score:
                comparing_player = sorted_players[i][0]
                stronger_player = self.find_stronger_player_on_draw(player, comparing_player)

                if stronger_player is None:
                    sorted_players[i].append(player)
                    has_player_been_inserted = True

                elif player is stronger_player:
                    sorted_players.insert(i, [player])
                    has_player_been_inserted = True

            if has_player_been_inserted:
                break

        if not has_player_been_inserted:
            sorted_players.append([player])

        return sorted_players

    @staticmethod
    def find_stronger_player_on_draw(player_1: TablePlayers, player_2: TablePlayers) -> Optional[TablePlayers]:
        nbr_of_cards = len(player_1.final_hand)

        for i in range(nbr_of_cards):
            if (player_1.final_hand[i].get_value()
                    > player_2.final_hand[i].get_value()):
                return player_1

            if (player_2.final_hand[i].get_value()
                    > player_1.final_hand[i].get_value()):
                return player_2

        return None

    def split_pot_among_players(self, players_grouped_by_strength: List[List[TablePlayers]]) -> Dict[TablePlayers, int]:
        players_pot_collections = {player: 0 for player in self._players}
        is_pot_collection = True

        while is_pot_collection:
            collecting_players = players_grouped_by_strength.pop(0)
            sub_pot = self.calculate_sub_pot(collecting_players, players_grouped_by_strength)

            if sub_pot is None:
                pot_division = self._pot / len(collecting_players)
                for player in collecting_players:
                    players_pot_collections[player] = int(pot_division)

                is_pot_collection = False

            else:
                individual_pot_collection = self.split_sub_pot_among_players(collecting_players, sub_pot)
                is_pot_collection = self.should_pot_collection_continue(collecting_players, players_grouped_by_strength)

                for player in collecting_players:
                    players_pot_collections[player] = int(individual_pot_collection[player])

                if is_pot_collection:
                    self.update_players_total_bet(collecting_players, players_grouped_by_strength)

        return players_pot_collections

    def calculate_sub_pot(self, collecting_players: List[TablePlayers],
                          players_grouped_by_strength: List[List[TablePlayers]]) -> Optional[int]:
        is_any_player_all_in = False
        sub_pot = 0

        for player in collecting_players:
            player_bet = player.total_bet
            sub_pot += player_bet

            if player.current_move is Moves.ALL_IN:
                is_any_player_all_in = True

        if not is_any_player_all_in:
            return None
        else:
            highest_bet = self.find_highest_player_bet(collecting_players)
            for player_group in players_grouped_by_strength:
                sub_pot += self.calculate_sub_pot_portion(player_group, highest_bet)

            return sub_pot

    @staticmethod
    def calculate_sub_pot_portion(players: List[TablePlayers], amount: int) -> int:
        sub_pot_portion = 0

        for player in players:
            if player.total_bet < amount:
                sub_pot_portion += player.total_bet
            else:
                sub_pot_portion += amount

        return sub_pot_portion

    def split_sub_pot_among_players(self, collecting_players: List[TablePlayers], sub_pot: int) \
            -> Dict[TablePlayers, int]:
        individual_pot_collection = {p: 0 for p in collecting_players}
        individual_over_bet = {p: 0 for p in collecting_players}
        lowest_bet = self.find_lowest_bet(collecting_players)
        actual_win = sub_pot

        for player in collecting_players:
            over_bet = player.total_bet - lowest_bet
            own_bet = player.total_bet

            individual_over_bet[player] = over_bet
            individual_pot_collection[player] += own_bet
            actual_win -= own_bet

        individual_win = actual_win / len(collecting_players)

        for player in collecting_players:
            individual_pot_collection[player] += individual_win

        return individual_pot_collection

    @staticmethod
    def find_lowest_bet(players: List[TablePlayers]) -> int:
        comparing_player = players[0]
        lowest_bet = comparing_player.total_bet

        for i in range(1, len(players)):
            if players[i].total_bet < lowest_bet:
                lowest_bet = players[i].total_bet

        return lowest_bet

    def should_pot_collection_continue(self, collecting_players: List[TablePlayers],
                                       players_grouped_by_strength: List[List[TablePlayers]]) -> bool:
        should_collection_continue = False
        highest_collecting_player_bet = 0

        for player in collecting_players:
            if player.total_bet > highest_collecting_player_bet:
                highest_collecting_player_bet = player.total_bet

        for player_group in players_grouped_by_strength:
            highest_not_collecting_player_bet = self.find_highest_player_bet(player_group)

            if highest_not_collecting_player_bet > highest_collecting_player_bet:
                should_collection_continue = True
                break

        return should_collection_continue

    @staticmethod
    def find_highest_player_bet(players: List[TablePlayers]) -> int:
        comparing_player = players[0]
        highest_bet = comparing_player.total_bet

        for i in range(1, len(players)):
            if players[i].total_bet > highest_bet:
                highest_bet = players[i].total_bet

        return highest_bet

    def update_players_total_bet(self, collecting_players: List[TablePlayers],
                                 players_grouped_by_strength: List[List[TablePlayers]]) -> None:
        highest_bet = self.find_highest_player_bet(collecting_players)

        for player_group in players_grouped_by_strength:
            self.reduce_players_total_bet(player_group, highest_bet)

    @staticmethod
    def reduce_players_total_bet(players: List[TablePlayers], amount: int) -> None:
        for player in players:
            if player.total_bet < amount:
                player.total_bet = 0
            else:
                player.total_bet -= amount

    def take_from_pot(self, amount: int) -> int:
        self._pot -= amount
        return amount

    def take_from_pot_leftover(self, amount: int) -> int:
        self._pot_leftover -= amount
        return amount

    def attach_observer(self, observer: BaseObserver) -> None:
        self._observers.attach(observer)

    def notify_observers(self, state: ObserverState) -> None:
        self._observers.notify(state)

    def print_player_info(self):
        print('--- PLAYER INFO ---')
        for player in self._players:
            hand = player.basic_player.get_hand()
            print('NAME:\t\t' + str(player.name))
            print('HAND:\t\t' + (str(hand[0].get_rank()) + ' ' + str(hand[0].get_suit()) + ', '
                  + str(hand[1].get_rank()) + ' ' + str(hand[1].get_suit()) if len(hand) > 0 else str(hand)))
            print('CURRENT_BET:\t' + str(player.current_bet))
            print('CURRENT_MOVE:\t' + str(player.current_move))
            print('CURRENT_CHIPS:\t' + str(player.basic_player.get_amount_of_chips()))
            print('SCORE:\t\t' + str(player.score))
            print('FINAL_HAND:\t' + str(player.final_hand_type))
            print()

    def print_state_info(self):
        cards = ''
        for card in self._community_cards:
            cards += '[' + str(card.get_rank()) + ' ' + str(card.get_suit() + '] ')

        print('--- STATE INFO ---')
        print('IS_ACTIVE:\t' + str(self._is_game_active))
        print('SMALL_BET:\t' + str(self._small_bet))
        print('BIG_BET:\t' + str(self._big_bet))
        print('POT:\t\t' + str(self._pot))
        print('DEALER:\t\t' + str(self._players.name))
        print('CURRENT_BET:\t' + str(self._current_bet))
        print('CURRENT_RAISE:\t' + str(self._current_raise))
        print('RAISE_CNT:\t' + str(self._raise_cnt))
        print('COMMUNITY_CARDS:' + cards)
        print()

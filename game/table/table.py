from .observer import State as ObserverState, BaseObserver
from .observers import Observers
from .players import Players as TablePlayers
from copy import deepcopy
from game import Card, Deck, Moves, Phases, Player as BasicPlayer, State, StrongestFinalHandFinder
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
        self._is_round_active = True
        self._is_game_active = True
        self._observers = Observers()
        self._players_who_lost = []
        self._current_phase = None

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

    def run_tournament(self) -> None:
        while self._is_game_active:
            self.init_pre_flop_phase()
            self.init_flop_phase()
            self.init_turn_phase()
            self.init_river_phase()
            self.init_showdown_phase()
            self.prepare_next_round()

    def init_pre_flop_phase(self) -> None:
        self._deck.shuffle()
        self.deal_cards()
        self.collect_blinds()
        self._current_raise = self._current_bet = self._small_bet

        self.init_betting_round(self._players.get_by_position(3))
        self._pot += self.take_from_pot_leftover(self._pot_leftover)

        self.update_round_active_state()

        self._current_phase = Phases.PRE_FLOP
        self._notify_observers()

    def init_flop_phase(self) -> None:
        self.deal_community_cards(3)

        if self._is_round_active:
            self.init_common_phase(self._small_bet)

        self._current_phase = Phases.FLOP
        self._notify_observers()

    def init_turn_phase(self) -> None:
        self.deal_community_cards()

        if self._is_round_active:
            self.init_common_phase(self._big_bet)

        self._current_phase = Phases.TURN
        self._notify_observers()

    def init_river_phase(self) -> None:
        self.deal_community_cards()

        if self._is_round_active:
            self.init_common_phase(self._big_bet)

        self._current_phase = Phases.RIVER
        self._notify_observers()

    def init_showdown_phase(self) -> None:
        # TO_DO: BREAK INTO 2 PHASES (SHOWDOWN, POT_COLLECTION)
        self.find_players_final_hand()
        self._current_phase = Phases.SHOWDOWN
        # NOTIFY OBSERVERS
        self.init_pot_collection()

    def prepare_next_round(self) -> None:
        self._define_next_dealer()
        self._kick_out_players_who_lost()
        self.update_game_active_state()

        if self._is_game_active:
            self._community_cards = []
            self._current_bet = 0
            self._current_raise = 0
            self._is_round_active = True
            self._raise_cnt = 0
            self._deck = Deck()

            for player in self._players:
                player.reset()

    def init_common_phase(self, bet_size: int) -> None:
        self.prepare_common_phase(bet_size)

        self.init_betting_round(self._players.next)

        self.update_round_active_state()

    def prepare_common_phase(self, bet_amount: int) -> None:
        self._current_raise = bet_amount
        self._raise_cnt = 0
        self._current_bet = 0

        for player in self._players:
            player.current_bet = 0
            if player.current_move is not Moves.FOLD and player.current_move is not Moves.ALL_IN:
                player.current_move = None

    def init_betting_round(self, stopping_player: TablePlayers) -> None:
        player = stopping_player

        while True:
            self.update_round_active_state()
            if not self._is_round_active:
                break

            moves = self.generate_player_moves(player)

            if moves is None:
                player = player.next
                if player is stopping_player:
                    break
                continue

            move = player.make_move(moves, self.generate_game_state())

            raise_cnt_before_move_execution = self._raise_cnt

            self.execute_player_move(player, move)

            if player.current_move is Moves.RAISE or (
                    player.current_move is Moves.ALL_IN and raise_cnt_before_move_execution != self._raise_cnt):
                stopping_player = player

            player = player.next

            if player is stopping_player:
                break

        for player in self._players:
            if player.current_move is Moves.ALL_IN and player.is_active:
                player.is_active = False

    def deal_cards(self) -> None:
        for _ in range(2):
            self.deal_one_round()

    def deal_community_cards(self, amount: int = 1):
        self._deck.burn()
        self._community_cards += self._deck.deal(amount)

    def deal_one_round(self) -> None:
        for player in self._players:
            player.receive_cards(self._deck.deal())

    def collect_blinds(self) -> None:
        player = self._players.next
        self.collect_blind(player, int(self._small_bet / 2))

        player = player.next
        self.collect_blind(player, self._small_bet)

        self._current_bet = self._small_bet

    def collect_blind(self, player: TablePlayers, blind: int) -> None:
        if player.get_amount_of_chips() > blind:
            self.collect_bet(player, blind)
        else:
            amount = player.get_amount_of_chips()
            self.collect_bet(player, amount)
            player.current_move = Moves.ALL_IN

    def collect_bet(self, player: TablePlayers, amount: int) -> None:
        self._pot += player.spend_chips(amount)
        player.current_bet += amount
        player.total_bet += amount

    def generate_player_moves(self, player: TablePlayers) -> Optional[List[Moves]]:
        moves = list()

        if player.current_move is Moves.FOLD or player.get_amount_of_chips() == 0:
            return None

        if player.current_bet < self._current_bet < player.get_amount_of_chips() + player.current_bet:
            moves.append(Moves.CALL)

        if player.get_amount_of_chips() + player.current_bet <= self._current_bet \
                or (player.get_amount_of_chips() + player.current_bet <= (self._current_bet + self._current_raise)
                    and not self.is_raising_capped()):
            moves.append(Moves.ALL_IN)

        if self._current_bet == player.current_bet:
            moves.append(Moves.CHECK)

        if not self.is_raising_capped() \
                and player.get_amount_of_chips() + player.current_bet > (self._current_bet + self._current_raise) \
                and self._players.count() - (
                len(self._players.find_by_move(Moves.FOLD)) + len(self._players.find_by_move(Moves.ALL_IN))) > 1:
            moves.append(Moves.RAISE)

        moves.append(Moves.FOLD)

        return moves

    def is_raising_capped(self) -> bool:
        return not self._raise_cnt < 4

    def generate_game_state(self) -> State:
        return State(
            community_cards=[Card(c.rank, c.suit, c.value) for c in self._community_cards],
            nbr_of_players=self._players.count() - len(self._players.find_by_move(Moves.FOLD)),
            current_phase=self._current_phase
        )

    def execute_player_move(self, player: TablePlayers, move: Moves) -> None:

        if move is Moves.CALL:
            amount = self.calculate_amount_to_call(player)
            self.collect_bet(player, amount)

        elif move is Moves.RAISE:
            amount = self.calculate_amount_to_raise(player)
            self.collect_bet(player, amount)
            self._current_bet = player.current_bet
            self._raise_cnt += 1

        elif move is Moves.ALL_IN:
            amount = player.get_amount_of_chips()
            self.collect_bet(player, amount)
            if self._current_bet < player.current_bet:
                self._raise_cnt += 1
                self._current_bet = player.current_bet
            else:
                player.is_active = False

        elif move is Moves.FOLD:
            player.is_active = False

        player.current_move = move

    def calculate_amount_to_call(self, player: TablePlayers) -> int:
        return self._current_bet - player.current_bet

    def calculate_amount_to_raise(self, player: TablePlayers) -> int:
        return self.calculate_amount_to_call(player) + self._current_raise

    def update_round_active_state(self) -> None:
        self._is_round_active = self._players.count_active() > 1

    def find_players_final_hand(self) -> None:

        for player in self._players:
            if player.current_move is not Moves.FOLD:
                final_hand = StrongestFinalHandFinder.find(self._community_cards + player.get_hand())

                player.final_hand = final_hand.hand
                player.final_hand_type = final_hand.type
                player.score = final_hand.score

    def init_pot_collection(self) -> None:
        sorted_players = self.sort_players_by_score()
        individual_pot_collection = self.split_pot_among_players(sorted_players)

        for player in individual_pot_collection:
            player.receive_chips(self.take_from_pot(individual_pot_collection[player]))

        self._pot_leftover += self.take_from_pot(self._pot)

        # NEED NEW PHASE: POT_COLLECTION
        self._current_phase = Phases.SHOWDOWN
        self._notify_observers(individual_pot_collection)

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
        if player_1.final_hand is None:
            return None

        for i, player_1_card in enumerate(player_1.final_hand):
            if player_1_card.value > player_2.final_hand[i].value:
                return player_1

            if player_2.final_hand[i].value > player_1_card.value:
                return player_2

        return None

    def split_pot_among_players(self, players_grouped_by_strength: List[List[TablePlayers]]) -> Dict[TablePlayers, int]:
        players_pot_collections = {player: 0 for player in self._players}
        is_pot_collection = True

        while is_pot_collection:
            collecting_players = players_grouped_by_strength.pop(0)
            sub_pot = self.calculate_sub_pot(collecting_players, players_grouped_by_strength)

            if sub_pot is None:
                pot = 0

                for player in self._players:
                    pot += player.total_bet

                pot_division = pot / len(collecting_players)

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

        for player in collecting_players:
            player.total_bet = 0

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

    def _define_next_dealer(self) -> None:
        for player in self._players:
            if player.next.get_amount_of_chips() > 0:
                self._players = player.next
                break

    def _kick_out_players_who_lost(self) -> None:
        players_who_lost = []

        for player in self._players:
            if player.get_amount_of_chips() == 0:
                players_who_lost.append(player)

        for player in players_who_lost:
            self._players.remove_player(player)
            self._players_who_lost.append(player)

    def update_game_active_state(self) -> None:
        self._is_game_active = not self.is_winner_present()

    def is_winner_present(self) -> bool:
        return self._players.count() == 1

    def attach_observer(self, observer: BaseObserver) -> None:
        self._observers.attach(observer)

    def _notify_observers(self, individual_pot_collection: Optional[Dict[TablePlayers, int]] = None) -> None:
        state = ObserverState(
            players=self._players.clone(),
            community_cards=deepcopy(self._community_cards),
            pot=self._pot,
            phase=self._current_phase,
            individual_pot_collection=individual_pot_collection
        )
        self._observers.notify(state)

    def print_player_info(self):
        print('--- PLAYER INFO ---')
        for player in self._players:
            hand = player.get_hand()
            print('NAME:\t\t' + str(player.name))
            print('HAND:\t\t' + (str(hand[0].rank) + ' ' + str(hand[0].suit) + ', '
                                 + str(hand[1].rank) + ' ' + str(hand[1].suit) if len(hand) > 0 else str(
                hand)))
            print('CURRENT_BET:\t' + str(player.current_bet))
            print('CURRENT_MOVE:\t' + str(player.current_move))
            print('CURRENT_CHIPS:\t' + str(player.get_amount_of_chips()))
            print('SCORE:\t\t' + str(player.score))
            print('FINAL_HAND:\t' + str(player.final_hand_type))
            print()

    def print_state_info(self):
        cards = ''
        for card in self._community_cards:
            cards += '[' + str(card.rank) + ' ' + str(card.suit + '] ')

        print('--- STATE INFO ---')
        print('IS_ACTIVE:\t' + str(self._is_round_active))
        print('SMALL_BET:\t' + str(self._small_bet))
        print('BIG_BET:\t' + str(self._big_bet))
        print('POT:\t\t' + str(self._pot))
        print('DEALER:\t\t' + str(self._players.name))
        print('CURRENT_BET:\t' + str(self._current_bet))
        print('CURRENT_RAISE:\t' + str(self._current_raise))
        print('RAISE_CNT:\t' + str(self._raise_cnt))
        print('COMMUNITY_CARDS:' + cards)
        print()

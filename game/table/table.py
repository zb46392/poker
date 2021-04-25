from .observer import State as ObserverState, BaseObserver
from .observers import Observers
from .players import Players as TablePlayers
from copy import deepcopy
from game import Card, Deck, Moves, Phases, State, StrongestFinalHandFinder
from game.player import Player as BasicPlayer
from typing import Dict, List, Optional, Tuple, Type


class Table:
    INIT_CHIPS = 100
    SMALL_BET = 2
    BIG_BET = 4

    def __init__(self, players_classes: List[Type[BasicPlayer]]) -> None:
        self._init_chips = self.INIT_CHIPS
        self._deck = Deck()
        self._players = self._create_players(players_classes)
        self._total_players = self._players.count()
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

    def run_tournament(self) -> None:
        while self._is_game_active:
            self._init_pre_flop_phase()
            self._init_flop_phase()
            self._init_turn_phase()
            self._init_river_phase()
            self._init_showdown_phase()
            self._init_pot_collection_phase()
            self._prepare_next_round()

    def reset_tournament(self) -> None:
        self._reset_players()
        self._reset_player_chips()
        self._reset_play()
        self._is_game_active = True

    def get_winner_name(self) -> str:
        if self._is_winner_present():
            return self._players.name
        return str(None)

    @property
    def player_names(self) -> List[str]:
        names = []
        for player in self._players:
            names.append(player.name)

        return names

    def attach_observer(self, observer: BaseObserver) -> None:
        self._observers.attach(observer)

    def detach_observer(self, observer: BaseObserver) -> None:
        self._observers.detach(observer)

    def _create_players(self, players_classes: List[Type[BasicPlayer]]) -> TablePlayers:
        if len(players_classes) < 2 or len(players_classes) > 10:
            raise ValueError('Only between 2 and 10 players allowed...')

        dealer = None
        previous_table_player = None

        for player_cnt in range(len(players_classes)):
            player_name = f'Player_{str(player_cnt + 1)} ({players_classes[player_cnt].__name__})'
            basic_player = players_classes[player_cnt](self._init_chips, player_name)

            if not isinstance(basic_player, BasicPlayer):
                raise ValueError('Class has to be extended from game.Player base class')

            table_player = TablePlayers(basic_player)

            if previous_table_player is not None:
                previous_table_player.next = table_player
            else:
                dealer = table_player

            previous_table_player = table_player

        previous_table_player.next = dealer

        return dealer

    def _init_pre_flop_phase(self) -> None:
        self._current_phase = Phases.PRE_FLOP

        self._deck.shuffle()
        self._deal_cards()
        self._collect_blinds()
        self._current_raise = self._current_bet = self._small_bet

        self._init_betting_round(self._players.get_by_position(3))

        self._update_round_active_state()

        self._notify_observers()

    def _init_flop_phase(self) -> None:
        self._current_phase = Phases.FLOP

        self._deal_community_cards(3)

        if self._is_round_active:
            self._init_common_phase(self._small_bet)

        self._notify_observers()

    def _init_turn_phase(self) -> None:
        self._current_phase = Phases.TURN

        self._deal_community_cards()

        if self._is_round_active:
            self._init_common_phase(self._big_bet)

        self._notify_observers()

    def _init_river_phase(self) -> None:
        self._current_phase = Phases.RIVER

        self._deal_community_cards()

        if self._is_round_active:
            self._init_common_phase(self._big_bet)

        self._notify_observers()

    def _init_showdown_phase(self) -> None:
        self._current_phase = Phases.SHOWDOWN

        self._find_players_final_hand()

        self._notify_observers()

    def _init_pot_collection_phase(self) -> None:
        self._current_phase = Phases.POT_COLLECTION

        sorted_players = self._sort_players_by_score()
        individual_pot_collection = self._split_pot_among_players(sorted_players)
        pot_leftover_collections = 0

        for player in self._players:
            if player in individual_pot_collection:
                collecting_chips = self._take_from_pot(individual_pot_collection[player])
                same_win_amount = list(individual_pot_collection.values()).count(individual_pot_collection[player])
                total_pot_leftover = self._pot_leftover * (pot_leftover_collections + 1)
                if self._pot_leftover > 0 and total_pot_leftover % same_win_amount == 0:
                    collecting_chips += self._take_from_pot_leftover(int(total_pot_leftover / same_win_amount))
                    pot_leftover_collections += 1

                player.receive_chips(collecting_chips)
            else:
                player.receive_chips(0)

        self._pot_leftover += self._take_from_pot(self._pot)

        self._notify_observers(individual_pot_collection)

    def _prepare_next_round(self) -> None:
        self._define_next_dealer()
        self._kick_out_players_who_lost()
        self._update_game_active_state()

        if self._is_game_active:
            self._reset_play()

    def _init_common_phase(self, bet_size: int) -> None:
        self._prepare_common_phase(bet_size)

        self._init_betting_round(self._players.next)

        self._update_round_active_state()

    def _prepare_common_phase(self, bet_amount: int) -> None:
        self._current_raise = bet_amount
        self._raise_cnt = 0
        self._current_bet = 0

        for player in self._players:
            player.current_bet = 0
            if player.current_move is not Moves.FOLD and player.current_move is not Moves.ALL_IN:
                player.current_move = None

    def _init_betting_round(self, stopping_player: TablePlayers) -> None:
        player = stopping_player

        while True:
            self._update_round_active_state()
            if not self._is_round_active:
                break

            moves = self._generate_player_moves(player)

            if moves is None:
                player = player.next
                if player is stopping_player:
                    break
                continue

            move = player.make_move(moves, self.generate_game_state(tuple(moves)))

            raise_cnt_before_move_execution = self._raise_cnt

            self._execute_player_move(player, move)

            if player.current_move is Moves.RAISE or (
                    player.current_move is Moves.ALL_IN and raise_cnt_before_move_execution != self._raise_cnt):
                stopping_player = player

            player = player.next

            if player is stopping_player:
                break

        for player in self._players:
            if player.current_move is Moves.ALL_IN and player.is_active:
                player.is_active = False

    def _deal_cards(self) -> None:
        for _ in range(2):
            self._deal_one_round()

    def _deal_community_cards(self, amount: int = 1):
        self._deck.burn()
        self._community_cards += self._deck.deal(amount)

    def _deal_one_round(self) -> None:
        for player in self._players:
            player.receive_cards(self._deck.deal())

    def _collect_blinds(self) -> None:
        player = self._players.next
        self._collect_blind(player, int(self._small_bet / 2))

        player = player.next
        self._collect_blind(player, self._small_bet)

        self._current_bet = self._small_bet

    def _collect_blind(self, player: TablePlayers, blind: int) -> None:
        if player.get_amount_of_chips() > blind:
            self._collect_bet(player, blind)
        else:
            amount = player.get_amount_of_chips()
            self._collect_bet(player, amount)
            player.current_move = Moves.ALL_IN

    def _collect_bet(self, player: TablePlayers, amount: int) -> None:
        self._pot += player.spend_chips(amount)
        player.current_bet += amount
        player.total_bet += amount

    def _generate_player_moves(self, player: TablePlayers) -> Optional[List[Moves]]:
        moves = list()

        if player.current_move is Moves.FOLD or player.get_amount_of_chips() == 0:
            return None

        if player.current_bet < self._current_bet < player.get_amount_of_chips() + player.current_bet:
            moves.append(Moves.CALL)

        if player.get_amount_of_chips() + player.current_bet <= self._current_bet \
                or (player.get_amount_of_chips() + player.current_bet <= (self._current_bet + self._current_raise)
                    and not self._is_raising_capped()):
            moves.append(Moves.ALL_IN)

        if self._current_bet == player.current_bet:
            moves.append(Moves.CHECK)

        if not self._is_raising_capped() \
                and player.get_amount_of_chips() + player.current_bet > (self._current_bet + self._current_raise) \
                and self._players.count() - (
                len(self._players.find_by_move(Moves.FOLD)) + len(self._players.find_by_move(Moves.ALL_IN))) > 1:
            moves.append(Moves.RAISE)

        moves.append(Moves.FOLD)

        return moves

    def _is_raising_capped(self) -> bool:
        return not self._raise_cnt < 4

    def generate_game_state(self, allowed_moves: Tuple[Moves]) -> State:
        return State(
            community_cards=tuple(Card(c.rank, c.suit, c.value) for c in self._community_cards),
            total_players=self._total_players,
            total_chips=self._total_players * self._init_chips,
            nbr_of_active_players=self._players.count() - len(self._players.find_by_move(Moves.FOLD)),
            current_phase=self._current_phase,
            is_raising_capped=self._is_raising_capped(),
            allowed_moves=allowed_moves,
            pot=self._pot,
            current_bet=self._current_bet
        )

    def _execute_player_move(self, player: TablePlayers, move: Moves) -> None:

        if move is Moves.CALL:
            amount = self._calculate_amount_to_call(player)
            self._collect_bet(player, amount)

        elif move is Moves.RAISE:
            amount = self._calculate_amount_to_raise(player)
            self._collect_bet(player, amount)
            self._current_bet = player.current_bet
            self._raise_cnt += 1

        elif move is Moves.ALL_IN:
            amount = player.get_amount_of_chips()
            self._collect_bet(player, amount)
            if self._current_bet < player.current_bet:
                self._raise_cnt += 1
                self._current_bet = player.current_bet
            else:
                player.is_active = False

        elif move is Moves.FOLD:
            player.is_active = False

        player.current_move = move

    def _calculate_amount_to_call(self, player: TablePlayers) -> int:
        return self._current_bet - player.current_bet

    def _calculate_amount_to_raise(self, player: TablePlayers) -> int:
        return self._calculate_amount_to_call(player) + self._current_raise

    def _update_round_active_state(self) -> None:
        total_players = self._players.count()
        folded_players = len(self._players.find_by_move(Moves.FOLD))
        not_folded_players = total_players - folded_players
        none_move_players = len(self._players.find_by_move(None))

        self._is_round_active = (self._players.count_active()) > 1 or (not_folded_players > 1 and none_move_players > 0)

    def _find_players_final_hand(self) -> None:

        for player in self._players:
            if player.current_move is not Moves.FOLD:
                final_hand = StrongestFinalHandFinder.find(self._community_cards + player.get_hand())

                player.final_hand = final_hand.hand
                player.final_hand_type = final_hand.type
                player.score = final_hand.score

    def _sort_players_by_score(self) -> List[List[TablePlayers]]:
        sorted_players = list()

        for player in self._players:
            sorted_players = self._insert_player_in_sorted_list(player, sorted_players)

        return sorted_players

    def _insert_player_in_sorted_list(self, player: TablePlayers, sorted_players: List[List[TablePlayers]]) \
            -> List[List[TablePlayers]]:
        has_player_been_inserted = False

        for i in range(len(sorted_players)):
            if player.score > self._players.find(sorted_players[i][0]).score:
                sorted_players.insert(i, [player])
                has_player_been_inserted = True

            elif player.score == self._players.find(sorted_players[i][0]).score:
                comparing_player = sorted_players[i][0]
                stronger_player = self._find_stronger_player_on_draw(player, comparing_player)

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
    def _find_stronger_player_on_draw(player_1: TablePlayers, player_2: TablePlayers) -> Optional[TablePlayers]:
        if player_1.final_hand is None:
            return None

        for i, player_1_card in enumerate(player_1.final_hand):
            if player_1_card.value > player_2.final_hand[i].value:
                return player_1

            if player_2.final_hand[i].value > player_1_card.value:
                return player_2

        return None

    def _split_pot_among_players(self, players_grouped_by_strength: List[List[TablePlayers]]) \
            -> Dict[TablePlayers, int]:
        players_pot_collections = {player: 0 for player in self._players}
        is_pot_collection = True

        while is_pot_collection:
            collecting_players = players_grouped_by_strength.pop(0)
            sub_pot = self._calculate_sub_pot(collecting_players, players_grouped_by_strength)

            if sub_pot is None:
                pot = 0

                for player in self._players:
                    pot += player.total_bet

                pot_division = pot / len(collecting_players)

                for player in collecting_players:
                    players_pot_collections[player] = int(pot_division)

                is_pot_collection = False

            else:
                individual_pot_collection = self._split_sub_pot_among_players(collecting_players)
                is_pot_collection = self._should_pot_collection_continue(collecting_players,
                                                                         players_grouped_by_strength)

                for player in collecting_players:
                    players_pot_collections[player] = int(individual_pot_collection[player])

                if is_pot_collection:
                    self._update_players_total_bet(collecting_players, players_grouped_by_strength)

        return players_pot_collections

    def _calculate_sub_pot(self, collecting_players: List[TablePlayers],
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
            highest_bet = self._find_highest_player_bet(collecting_players)
            for player_group in players_grouped_by_strength:
                sub_pot += self._calculate_sub_pot_portion(player_group, highest_bet)

            return sub_pot

    @staticmethod
    def _calculate_sub_pot_portion(players: List[TablePlayers], amount: int) -> int:
        sub_pot_portion = 0

        for player in players:
            if player.total_bet < amount:
                sub_pot_portion += player.total_bet
            else:
                sub_pot_portion += amount

        return sub_pot_portion

    def _split_sub_pot_among_players(self, collecting_players: List[TablePlayers]) -> Dict[TablePlayers, int]:
        individual_pot_collection = {p: 0 for p in collecting_players}
        highest_bet = self._find_highest_player_bet(collecting_players)
        players_bets_asc = [{
            'bet': highest_bet,
            'total_players': 0,
            'collecting_players': 0
        }]

        for player in self._players:
            index = None
            for i, player_bet in enumerate(players_bets_asc):
                if player.total_bet < player_bet['bet']:
                    index = i
                    break

            if index is not None:
                players_bets_asc.insert(index, {
                    'bet': player.total_bet,
                    'total_players': 0,
                    'collecting_players': 0
                })

        for player in self._players:
            for player_bet in players_bets_asc:
                if player.total_bet == player_bet['bet']:
                    player_bet['total_players'] += 1
                    if player in collecting_players:
                        player_bet['collecting_players'] += 1
                    break

                if player.total_bet > player_bet['bet']:
                    player_bet['total_players'] += 1
                    if player in collecting_players:
                        player_bet['collecting_players'] += 1

        for player in collecting_players:
            sub = 0
            for player_bet in players_bets_asc:
                if player.total_bet >= player_bet['bet']:
                    individual_pot_collection[player] += \
                        ((player_bet['bet'] - sub) * player_bet['total_players']) / player_bet['collecting_players']
                sub = player_bet['bet']

        return individual_pot_collection

    @staticmethod
    def _find_lowest_bet(players: List[TablePlayers]) -> int:
        comparing_player = players[0]
        lowest_bet = comparing_player.total_bet

        for i in range(1, len(players)):
            if players[i].total_bet < lowest_bet:
                lowest_bet = players[i].total_bet

        return lowest_bet

    def _should_pot_collection_continue(self, collecting_players: List[TablePlayers],
                                        players_grouped_by_strength: List[List[TablePlayers]]) -> bool:
        should_collection_continue = False
        highest_collecting_player_bet = 0

        for player in collecting_players:
            if player.total_bet > highest_collecting_player_bet:
                highest_collecting_player_bet = player.total_bet

        for player_group in players_grouped_by_strength:
            highest_not_collecting_player_bet = self._find_highest_player_bet(player_group)

            if highest_not_collecting_player_bet > highest_collecting_player_bet:
                should_collection_continue = True
                break

        return should_collection_continue

    @staticmethod
    def _find_highest_player_bet(players: List[TablePlayers]) -> int:
        comparing_player = players[0]
        highest_bet = comparing_player.total_bet

        for i in range(1, len(players)):
            if players[i].total_bet > highest_bet:
                highest_bet = players[i].total_bet

        return highest_bet

    def _update_players_total_bet(self, collecting_players: List[TablePlayers],
                                  players_grouped_by_strength: List[List[TablePlayers]]) -> None:
        highest_bet = self._find_highest_player_bet(collecting_players)

        for player in collecting_players:
            player.total_bet = 0

        for player_group in players_grouped_by_strength:
            self._reduce_players_total_bet(player_group, highest_bet)

    @staticmethod
    def _reduce_players_total_bet(players: List[TablePlayers], amount: int) -> None:
        for player in players:
            if player.total_bet < amount:
                player.total_bet = 0
            else:
                player.total_bet -= amount

    def _take_from_pot(self, amount: int) -> int:
        self._pot -= amount
        return amount

    def _take_from_pot_leftover(self, amount: int) -> int:
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

    def _reset_play(self) -> None:
        self._community_cards = []
        self._current_bet = 0
        self._current_raise = 0
        self._is_round_active = True
        self._raise_cnt = 0
        self._deck = Deck()

        for player in self._players:
            player.reset()

    def _update_game_active_state(self) -> None:
        self._is_game_active = not self._is_winner_present()

    def _is_winner_present(self) -> bool:
        return self._players.count() == 1

    def _reset_players(self) -> None:
        players = []

        for p in self._players_who_lost:
            players.append(p)

        for p in self._players:
            players.append(p)

        np = None
        for p in players:
            if np is not None:
                np.next = p
            np = p
        np.next = players[0]
        self._players = np.next
        self._players_who_lost = []

    def _reset_player_chips(self) -> None:
        for p in self._players:
            a = p.get_amount_of_chips()
            p.spend_chips(a)
            p.receive_chips(self._init_chips)

    def _notify_observers(self, individual_pot_collection: Optional[Dict[TablePlayers, int]] = None) -> None:
        state = ObserverState(
            players=self._players,
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

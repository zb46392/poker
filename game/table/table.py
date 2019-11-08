from game import Deck
from game import Player
from enum import Enum


class Table:
    INIT_CHIPS = 100
    SMALL_BET = 2
    BIG_BET = 4

    class Moves(Enum):
        CALL = 1
        CHECK = 2
        FOLD = 3
        RAISE = 4
        ALL_IN = 5

    class FinalHandMultipliers(Enum):
        HIGH_CARD = 1
        PAIR = 20
        TWO_PAIRS = 300
        TRIS = 4000
        STRAIGHT = 15000
        FLUSH = 33000
        FULL_HOUSE = 500000
        POKER = 6600000
        STRAIGHT_FLUSH = 21500000
        ROYAL_FLUSH = 22000000

    def __init__(self, list_of_players_classes: list):

        self.deck = Deck()
        self.dealer = None
        self.players = self.init_players(list_of_players_classes)
        self.pot = 0
        self.pot_leftover = 0
        self.community_cards = list()
        self.current_bet = 0
        self.small_bet = self.SMALL_BET
        self.big_bet = self.BIG_BET
        self.current_raise = self.small_bet
        self.raise_cnt = 0
        self.is_game_active = True

    def init_players(self, list_of_players_classes: list):
        if len(list_of_players_classes) < 2 or len(list_of_players_classes) > 10:
            raise ValueError('Only between 2 and 10 players allowed...')

        players = dict()
        previous_player = None

        for player_cnt in range(len(list_of_players_classes)):
            player = list_of_players_classes[player_cnt](self.INIT_CHIPS)

            if not isinstance(player, Player):
                raise ValueError('Class has to be extended from Player base class')

            players[player] = {
                'current_bet': 0,
                'total_bet': 0,
                'current_move': None,
                'name': 'Player_' + str(player_cnt+1),
                'final_hand': None,
                'final_hand_type': None,
                'score': 0
            }

            if previous_player is not None:
                players[previous_player]['next_player'] = player
            else:
                self.dealer = player

            previous_player = player

        players[previous_player]['next_player'] = self.dealer

        return players

    def init_pre_flop_phase(self):
        self.deck.shuffle()
        self.deal_cards()
        self.collect_blinds()
        self.current_raise = self.current_bet = self.small_bet

        self.init_betting_round(self.get_next_player(self.dealer, position=3))
        self.pot += self.take_from_pot_leftover(self.pot_leftover)

        self.update_game_active_state()

    def init_flop_phase(self):
        if self.is_game_active:
            self.init_common_phase(self.small_bet, cards_to_deal=3)

    def init_turn_phase(self):
        if self.is_game_active:
            self.init_common_phase(self.big_bet)

    def init_river_phase(self):
        if self.is_game_active:
            self.init_common_phase(self.big_bet)

    def init_showdown_phase(self):
        self.find_players_final_hand()
        self.init_pot_collection()

    def deal_cards(self):
        for _ in range(2):
            self.deal_one_round()

    def deal_one_round(self):
        for player in self.players:
            player.receive_cards(self.deck.deal())

    def collect_blinds(self):
        player = self.get_next_player(self.dealer)
        self.collect_blind(player, int(self.small_bet / 2))

        player = self.get_next_player(player)
        self.collect_blind(player, self.small_bet)

        self.current_bet = self.small_bet

    def collect_blind(self, player: Player, blind: int):
        if player.get_amount_of_chips() > blind:
            self.collect_bet(player, blind)
            self.players[player]['current_bet'] = blind
        else:
            amount = player.get_amount_of_chips()
            self.collect_bet(player, amount)
            self.players[player]['current_bet'] = amount
            self.players[player]['current_move'] = self.Moves.ALL_IN

    def collect_bet(self, player: Player, amount: int):
        self.pot += player.spend_chips(amount)

    def get_next_player(self, current_player: Player, position=1):
        player = current_player
        for _ in range(position):
            player = self.players[player]['next_player']

        return player

    def get_dealer(self):
        return self.dealer

    def init_betting_round(self, stopping_player: Player):
        player = stopping_player

        while True:
            if self.have_all_folded_but_one():
                self.is_game_active = False
                break

            moves = self.generate_player_moves(player)

            if moves is None:
                player = self.get_next_player(player)
                if player is stopping_player:
                    break
                continue

            move = player.make_move(moves, self.generate_game_state())

            self.execute_player_move(player, move)
            if self.players[player]['current_bet'] > self.current_bet:
                stopping_player = player
                self.current_bet = self.players[player]['current_bet']

            player = self.get_next_player(player)

            if player is stopping_player:
                break

    def have_all_folded_but_one(self):
        if self.count_folded_players() < len(self.players) - 1:
            return False
        else:
            return True

    def count_folded_players(self):
        folded_players = 0

        for player in self.players:
            if self.players[player]['current_move'] is self.Moves.FOLD:
                folded_players += 1

        return folded_players

    def generate_player_moves(self, player: Player):
        moves = list()

        if self.players[player]['current_move'] is self.Moves.FOLD \
                or self.players[player]['current_move'] is self.Moves.ALL_IN:
            return None

        if self.players[player]['current_bet'] < self.current_bet < player.get_amount_of_chips():
            moves.append(self.Moves.CALL)

        if player.get_amount_of_chips() <= self.current_bet \
                or (player.get_amount_of_chips() <= (self.current_bet + self.current_raise)
                    and not self.is_raising_capped()):
            moves.append(self.Moves.ALL_IN)

        if self.current_bet == self.players[player]['current_bet']:
            moves.append(self.Moves.CHECK)

        if not self.is_raising_capped() and player.get_amount_of_chips() > (self.current_bet + self.current_raise):
            moves.append(self.Moves.RAISE)

        moves.append(self.Moves.FOLD)

        return moves

    def is_raising_capped(self):
        return not self.raise_cnt < 4

    def generate_game_state(self):
        return {'community_cards': self.community_cards}

    def execute_player_move(self, player: Player, move: Moves):

        if move is self.Moves.CALL:
            amount = self.calculate_amount_to_call(player)
            self.collect_bet(player, amount)
            self.players[player]['current_bet'] += amount
            self.players[player]['total_bet'] += amount

        elif move is self.Moves.RAISE:
            amount = self.calculate_amount_to_raise(player)
            self.collect_bet(player, amount)
            self.players[player]['current_bet'] += amount
            self.players[player]['total_bet'] += amount
            self.current_bet += self.current_raise
            self.raise_cnt += 1

        elif move is self.Moves.ALL_IN:
            amount = player.get_amount_of_chips()
            self.collect_bet(player, amount)
            self.players[player]['current_bet'] += amount
            self.players[player]['total_bet'] += amount

        self.players[player]['current_move'] = move

    def calculate_amount_to_call(self, player: Player):
        return self.current_bet - self.players[player]['current_bet']

    def calculate_amount_to_raise(self, player: Player):
        return self.calculate_amount_to_call(player) + self.current_raise

    def update_game_active_state(self):
        if self.have_all_folded_but_one():
            self.is_game_active = False

    def init_common_phase(self, bet_size: int, cards_to_deal: int = 1):
        self.prepare_common_phase(bet_size)

        self.deck.burn()
        self.community_cards += self.deck.deal(cards_to_deal)
        self.init_betting_round(self.get_next_player(self.dealer))

        self.update_game_active_state()

    def prepare_common_phase(self, bet_amount: int):
        self.current_raise = bet_amount
        self.raise_cnt = 0
        self.current_bet = 0

    def find_players_final_hand(self):

        for player in self.players:
            if self.players[player]['current_move'] is self.Moves.FOLD:
                final_hand = {'final_hand': None, 'final_hand_type': None, 'score': 0}
            else:
                final_hand = self.find_strongest_final_hand(self.community_cards + player.get_hand())

            self.players[player]['final_hand'] = final_hand['final_hand']
            self.players[player]['final_hand_type'] = final_hand['final_hand_type']
            self.players[player]['score'] = final_hand['score']

    def find_strongest_final_hand(self, hand: list):
        hand.sort(reverse=True)
        final_hand = self.try_find_flush(hand)

        if final_hand is not None:
            bigger_hand = self.try_find_straight(final_hand['final_hand'])
            if bigger_hand is not None:
                if self.is_royal_flush(bigger_hand['final_hand']):
                    return self.create_final_hand(bigger_hand['final_hand'], self.FinalHandMultipliers.ROYAL_FLUSH)
                else:
                    return self.create_final_hand(bigger_hand['final_hand'], self.FinalHandMultipliers.STRAIGHT_FLUSH)
            else:
                return final_hand

        final_hand = self.try_find_poker(hand)
        if final_hand is not None:
            return final_hand

        final_hand = self.try_find_full_house(hand)
        if final_hand is not None:
            return final_hand

        final_hand = self.try_find_straight(hand)
        if final_hand is not None:
            return final_hand

        final_hand = self.try_find_tris(hand)
        if final_hand is not None:
            return final_hand

        final_hand = self.try_find_two_pair(hand)
        if final_hand is not None:
            return final_hand

        final_hand = self.try_find_pair(hand)
        if final_hand is not None:
            return final_hand

        return self.create_final_hand(hand[:5], self.FinalHandMultipliers.HIGH_CARD)

    def create_final_hand(self, hand, hand_type):
        if hand_type is self.FinalHandMultipliers.TWO_PAIRS or hand_type is self.FinalHandMultipliers.FULL_HOUSE:
            score = hand[0].get_value() * hand_type.value + hand[3].get_value()
        else:
            score = hand[0].get_value() * hand_type.value

        return {
            'final_hand': hand,
            'final_hand_type': hand_type,
            'score': score
        }

    def try_find_flush(self, sorted_cards):
        suits = dict()

        for card in sorted_cards:
            if card.get_suit() not in suits:
                suits[card.get_suit()] = list()

            suits[card.get_suit()].append(card)

        for suit in suits:
            if len(suits[suit]) >= 5:
                return self.create_final_hand(suits[suit][:5], self.FinalHandMultipliers.FLUSH)

        return None

    def try_find_straight(self, sorted_cards):
        cnt = 0
        previous_card = sorted_cards[0]

        for i in range(1, len(sorted_cards)):
            if sorted_cards[i].get_value() != previous_card.get_value() - 1:
                cnt = 0
            else:
                cnt += 1
                if cnt == 4:
                    return self.create_final_hand(sorted_cards[i-4:i+1], self.FinalHandMultipliers.STRAIGHT)

            previous_card = sorted_cards[i]

        if cnt == 3 and sorted_cards[0].get_value() == 13 and sorted_cards[-1].get_value() == 1:
            return self.create_final_hand(sorted_cards[len(sorted_cards) - 4:-1] + [sorted_cards[0]],
                                          self.FinalHandMultipliers.STRAIGHT)

        return None

    @staticmethod
    def is_royal_flush(cards):
        return (cards[0].get_value() == 13
                and cards[1].get_value() == 12
                and cards[2].get_value() == 11
                and cards[3].get_value() == 10
                and cards[4].get_value() == 9
                and cards[0].get_suit()
                == cards[1].get_suit()
                == cards[2].get_suit()
                == cards[3].get_suit()
                == cards[4].get_suit())

    def try_find_poker(self, sorted_cards):
        same_value_cards = self.find_same_value_cards(sorted_cards, 4)

        if same_value_cards is not None:
            high_value_card = self.find_high_value_cards_not_in_cards(same_value_cards, sorted_cards, 1)
            return self.create_final_hand(same_value_cards + high_value_card, self.FinalHandMultipliers.POKER)

        return None

    def find_same_value_cards(self, cards, amount):
        cards_by_value = self.divide_cards_by_value(cards)

        for same_value_cards in cards_by_value:
            if len(cards_by_value[same_value_cards]) >= amount:
                return cards_by_value[same_value_cards][:amount]

        return None

    @staticmethod
    def divide_cards_by_value(cards):
        same_value_cards = dict()

        for card in cards:
            if card.get_value() not in same_value_cards:
                same_value_cards[card.get_value()] = list()

            same_value_cards[card.get_value()].append(card)

        return same_value_cards

    @staticmethod
    def find_high_value_cards_not_in_cards(selected_cards, cards, amount):
        high_value_cards = list()
        for card in cards:
            if card not in selected_cards:
                high_value_cards.append(card)
                if len(high_value_cards) == amount:
                    return high_value_cards

    def try_find_full_house(self, sorted_cards):
        same_3_cards = self.find_same_value_cards(sorted_cards, 3)

        if same_3_cards is not None:
            same_2_cards = self.find_same_value_cards([card for card in sorted_cards if card not in same_3_cards], 2)

            if same_2_cards is not None:
                return self.create_final_hand(same_3_cards + same_2_cards, self.FinalHandMultipliers.FULL_HOUSE)

        return None

    def try_find_tris(self, sorted_cards):
        same_value_cards = self.find_same_value_cards(sorted_cards, 3)

        if same_value_cards is not None:
            high_value_cards = self.find_high_value_cards_not_in_cards(same_value_cards, sorted_cards, 2)
            return self.create_final_hand(same_value_cards + high_value_cards, self.FinalHandMultipliers.TRIS)

        return None

    def try_find_two_pair(self, sorted_cards):
        first_pair = self.find_same_value_cards(sorted_cards, 2)

        if first_pair is not None:
            second_pair = self.find_same_value_cards([card for card in sorted_cards if card not in first_pair], 2)

            if second_pair is not None:
                high_value_cards = self.find_high_value_cards_not_in_cards(first_pair + second_pair, sorted_cards, 1)
                return self.create_final_hand(first_pair + second_pair + high_value_cards,
                                              self.FinalHandMultipliers.TWO_PAIRS)

        return None

    def try_find_pair(self, sorted_cards):
        same_value_cards = self.find_same_value_cards(sorted_cards, 2)

        if same_value_cards is not None:
            high_value_cards = self.find_high_value_cards_not_in_cards(same_value_cards, sorted_cards, 3)
            return self.create_final_hand(same_value_cards + high_value_cards, self.FinalHandMultipliers.PAIR)

        return None

    def init_pot_collection(self):
        sorted_players = self.sort_players_by_score()
        individual_pot_collection = self.split_pot_among_players(sorted_players)

        for player in individual_pot_collection:
            player.receive_chips(self.take_from_pot(individual_pot_collection[player]))

        self.pot_leftover += self.take_from_pot(self.pot)

    def sort_players_by_score(self):
        sorted_players = list()

        for player in self.players:
            sorted_players = self.insert_player_in_sorted_list(player, sorted_players)

        return sorted_players

    def insert_player_in_sorted_list(self, player: Player, sorted_players: list):
        has_player_been_inserted = False

        for i in range(len(sorted_players)):
            if self.players[player]['score'] > self.players[sorted_players[i][0]]['score']:
                sorted_players.insert(i, [player])
                has_player_been_inserted = True

            elif self.players[player]['score'] == self.players[sorted_players[i][0]]['score']:
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

    def find_stronger_player_on_draw(self, player_1: Player, player_2: Player):
        nbr_of_cards = len(self.players[player_1]['final_hand'])

        for i in range(nbr_of_cards):
            if (self.players[player_1]['final_hand'][i].get_value()
                    > self.players[player_2]['final_hand'][i].get_value()):
                return player_1

            if (self.players[player_2]['final_hand'][i].get_value()
                    > self.players[player_1]['final_hand'][i].get_value()):
                return player_2

        return None

    def split_pot_among_players(self, players_grouped_by_strength: list):
        players_pot_collections = {player: 0 for player in self.players}
        is_pot_collection = True

        while is_pot_collection:
            collecting_players = players_grouped_by_strength.pop(0)
            sub_pot = self.calculate_sub_pot(collecting_players, players_grouped_by_strength)

            if sub_pot is None:
                pot_division = self.pot / len(collecting_players)
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

    def calculate_sub_pot(self, collecting_players: list, players_grouped_by_strength: list):
        is_any_player_all_in = False
        sub_pot = 0

        for player in collecting_players:
            player_bet = self.players[player]['total_bet']
            sub_pot += player_bet

            if self.players[player]['current_move'] is self.Moves.ALL_IN:
                is_any_player_all_in = True

        if not is_any_player_all_in:
            return None
        else:
            highest_bet = self.find_highest_player_bet(collecting_players)
            for player_group in players_grouped_by_strength:
                sub_pot += self.calculate_sub_pot_portion(player_group, highest_bet)

            return sub_pot

    def calculate_sub_pot_portion(self, players: list, amount: int):
        sub_pot_portion = 0

        for player in players:
            if self.players[player]['total_bet'] < amount:
                sub_pot_portion += self.players[player]['total_bet']
            else:
                sub_pot_portion += amount

        return sub_pot_portion

    def split_sub_pot_among_players(self, collecting_players: list, sub_pot: int):
        individual_pot_collection = {p: 0 for p in collecting_players}
        individual_over_bet = {p: 0 for p in collecting_players}
        lowest_bet = self.find_lowest_bet(collecting_players)
        actual_win = sub_pot

        for player in collecting_players:
            over_bet = self.players[player]['total_bet'] - lowest_bet
            own_bet = self.players[player]['total_bet']

            individual_over_bet[player] = over_bet
            individual_pot_collection[player] += own_bet
            actual_win -= own_bet

        individual_win = actual_win / len(collecting_players)

        for player in collecting_players:
            individual_pot_collection[player] += individual_win

        return individual_pot_collection

    def find_lowest_bet(self, players: list):
        comparing_player = players[0]
        lowest_bet = self.players[comparing_player]['total_bet']

        for i in range(1, len(players)):
            if self.players[players[i]]['total_bet'] < lowest_bet:
                lowest_bet = self.players[players[i]]['total_bet']

        return lowest_bet

    def should_pot_collection_continue(self, collecting_players: list, players_grouped_by_strength: list):
        should_collection_continue = False
        highest_collecting_player_bet = 0

        for player in collecting_players:
            if self.players[player]['total_bet'] > highest_collecting_player_bet:
                highest_collecting_player_bet = self.players[player]['total_bet']

        for player_group in players_grouped_by_strength:
            highest_not_collecting_player_bet = self.find_highest_player_bet(player_group)

            if highest_not_collecting_player_bet > highest_collecting_player_bet:
                should_collection_continue = True
                break

        return should_collection_continue

    def find_highest_player_bet(self, players: list):
        comparing_player = players[0]
        highest_bet = self.players[comparing_player]['total_bet']

        for i in range(1, len(players)):
            if self.players[players[i]]['total_bet'] > highest_bet:
                highest_bet = self.players[players[i]]['total_bet']

        return highest_bet

    def update_players_total_bet(self, collecting_players: list, players_grouped_by_strength: list):
        highest_bet = self.find_highest_player_bet(collecting_players)

        for player_group in players_grouped_by_strength:
            self.reduce_players_total_bet(player_group, highest_bet)

    def reduce_players_total_bet(self, players: list, amount: int):
        for player in players:
            if self.players[player]['total_bet'] < amount:
                self.players[player]['total_bet'] = 0
            else:
                self.players[player]['total_bet'] -= amount

    def take_from_pot(self, amount: int):
        self.pot -= amount
        return amount

    def take_from_pot_leftover(self, amount: int):
        self.pot_leftover -= amount
        return amount

    def print_player_info(self):
        print('--- PLAYER INFO ---')
        for player in self.players:
            hand = player.get_hand()
            print('NAME:\t\t' + str(self.players[player]['name']))
            print('HAND:\t\t' + (str(hand[0].get_rank()) + ' ' + str(hand[0].get_suit()) + ', '
                  + str(hand[1].get_rank()) + ' ' + str(hand[1].get_suit()) if len(hand) > 0 else str(hand)))
            print('CURRENT_BET:\t' + str(self.players[player]['current_bet']))
            print('CURRENT_MOVE:\t' + str(self.players[player]['current_move']))
            print('CURRENT_CHIPS:\t' + str(player.get_amount_of_chips()))
            print('SCORE:\t\t' + str(self.players[player]['score']))
            print('FINAL_HAND:\t' + str(self.players[player]['final_hand_type']))
            print()

    def print_state_info(self):
        cards = ''
        for card in self.community_cards:
            cards += '[' + str(card.get_rank()) + ' ' + str(card.get_suit() + '] ')

        print('--- STATE INFO ---')
        print('IS_ACTIVE:\t' + str(self.is_game_active))
        print('SMALL_BET:\t' + str(self.small_bet))
        print('BIG_BET:\t' + str(self.big_bet))
        print('POT:\t\t' + str(self.pot))
        print('DEALER:\t\t' + str(self.players[self.dealer]['name']))
        print('CURRENT_BET:\t' + str(self.current_bet))
        print('CURRENT_RAISE:\t' + str(self.current_raise))
        print('RAISE_CNT:\t' + str(self.raise_cnt))
        print('COMMUNITY_CARDS:' + cards)
        print()

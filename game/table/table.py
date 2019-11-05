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

    def __init__(self, list_of_players_classes):

        self.deck = Deck()
        self.dealer = None
        self.players = self.init_players(list_of_players_classes)
        self.big_blind_player = None
        self.pot = 0
        self.community_cards = list()
        self.current_bet = 0
        self.highest_better = None
        self.small_bet = Table.SMALL_BET
        self.big_bet = Table.BIG_BET
        self.current_raise = self.small_bet
        self.raise_cnt = 0
        self.is_game_active = True

    def init_players(self, list_of_players_classes):
        if len(list_of_players_classes) < 2 or len(list_of_players_classes) > 10:
            raise ValueError('Only between 2 and 10 players allowed...')

        players = dict()
        previous_player = None
        player_cnt = 0

        for player_class in list_of_players_classes:
            player = player_class(Table.INIT_CHIPS)

            if not isinstance(player, Player):
                raise ValueError('Class has to be extended from Player base class')

            players[player] = {'current_bet': 0, 'current_move': None, 'name': 'Player_' + str(player_cnt)}

            if previous_player is not None:
                players[previous_player]['next_player'] = player
            else:
                self.dealer = player

            previous_player = player
            player_cnt += 1

        players[previous_player]['next_player'] = self.dealer

        return players

    def init_preflop_phase(self):
        self.deck.shuffle()
        self.deal_cards()
        self.collect_blinds()
        self.current_raise = self.small_bet

        self.init_betting_round(self.get_next_player(self.highest_better))
        self.big_blind_player = None

        if self.have_all_folded_but_one():
            self.is_game_active = False

    def init_flop_phase(self):
        pass
        '''
        burn card
        flop
        player action
        '''

    def init_turn_phase(self):
        pass
        '''
        burn card 
        turn
        player action
        '''

    def init_river_phase(self):
        pass
        '''
        burn card
        river
        player action
        '''

    def init_showdown_phase(self):
        pass
        '''
        ??? option to show or discard cards
        player recieves pot ( or split if draw )
        '''
    def deal_cards(self):
        for _ in range(2):
            self.deal_one_round()

    def deal_one_round(self):
        for player in self.players:
            player.receive_card(self.deck.deal())

    def collect_blinds(self):
        player = self.get_next_player(self.dealer)
        self.collect_blind(player, int(self.small_bet / 2))

        player = self.get_next_player(player)
        self.collect_blind(player, self.small_bet)

        self.highest_better = player
        self.big_blind_player = player
        self.current_bet = self.small_bet

    def collect_blind(self, player: Player, blind: int):
        if player.get_amount_of_chips() > blind:
            self.collect_bet(player, blind)
            self.players[player]['current_bet'] = blind
        else:
            amount = player.get_amount_of_chips()
            self.collect_bet(player, amount)
            self.players[player]['current_bet'] = amount
            self.players[player]['current_move'] = Table.Moves.ALL_IN

    def collect_bet(self, player: Player, amount: int):
        self.pot += player.spend_chips(amount)

    def get_next_player(self, current_player: Player):
        return self.players[current_player]['next_player']

    def get_dealer(self):
        return self.dealer

    def init_betting_round(self, player: Player):

        while player is not self.highest_better or self.players[player]['current_move'] is None:
            if self.have_all_folded_but_one():
                self.is_game_active = False
                break

            moves = self.generate_player_moves(player)

            if moves is None:
                player = self.get_next_player(player)
                continue

            move = player.make_move(moves, self.generate_game_state())

            self.execute_player_move(player, move)

            if self.big_blind_player is None or player is not self.big_blind_player:
                player = self.get_next_player(player)

    def have_all_folded_but_one(self):
        if self.count_folded_players() < len(self.players) - 1:
            return False
        else:
            return True

    def count_folded_players(self):
        folded_players = 0

        for player in self.players:
            if self.players[player]['current_move'] is Table.Moves.FOLD:
                folded_players += 1

        return folded_players

    '''
     AFTER SHOWDOWN (POT COLLECTION):
     
         for player in players_sorted_by_hand_strength:
            if player.action is ALL_IN ----> SPLIT POT SPECIAL CASE !!!
                player.receive_chips(take_chips_from_pot( CALCULATE_AMOUNT )) ---> needs proper func name
            else:
                player.receive_chips(take_whole_pot())
                break
                
        CALCULATE_AMOUNT(me_player):
            amount = 0
            
            for player in all_players:
                if player.get_bet() < me_player.get_bet():
                    amount += player.get_bet()
                else:
                    amount += me_player.get_bet()
            
            return amount
        
        PLAYER KICKED OUT OF PLAY
        if player kicked out -> prevoius players next player is next player
    '''
    def generate_player_moves(self, player: Player):
        moves = list()

        if self.players[player]['current_move'] is Table.Moves.FOLD \
                or self.players[player]['current_move'] is Table.Moves.ALL_IN:
            return None

        if self.players[player]['current_bet'] < self.current_bet < player.get_amount_of_chips():
            moves.append(Table.Moves.CALL)

        if player.get_amount_of_chips() <= self.current_bet \
                or (player.get_amount_of_chips() <= (self.current_bet + self.current_raise)
                    and not self.is_raising_capped()):
            moves.append(Table.Moves.ALL_IN)

        if self.current_bet == self.players[player]['current_bet']:
            moves.append(Table.Moves.CHECK)

        if not self.is_raising_capped() and player.get_amount_of_chips() > (self.current_bet + self.current_raise):
            moves.append(Table.Moves.RAISE)

        moves.append(Table.Moves.FOLD)

        return moves

    def is_raising_capped(self):
        return not self.raise_cnt < 4

    def generate_game_state(self):
        return {'community_cards': self.community_cards}

    def execute_player_move(self, player: Player, move: Moves):

        if move is Table.Moves.CALL:
            amount = self.calculate_amount_to_call(player)
            self.collect_bet(player, amount)
            self.players[player]['current_bet'] += amount

        elif move is Table.Moves.RAISE:
            amount = self.calculate_amount_to_raise(player)
            self.collect_bet(player, amount)
            self.players[player]['current_bet'] += amount
            self.highest_better = player
            self.raise_cnt += 1

        elif move is Table.Moves.ALL_IN:
            amount = player.get_amount_of_chips()
            self.collect_bet(player, amount)
            self.players[player]['current_bet'] += amount

        self.players[player]['current_move'] = move

    def calculate_amount_to_call(self, player: Player):
        return self.current_bet - self.players[player]['current_bet']

    def calculate_amount_to_raise(self, player: Player):
        return self.calculate_amount_to_call(player) + self.current_raise

    def print_player_info(self):
        print('--- PLAYER INFO ---')
        for player in self.players:
            hand = player.show_hand()
            print('NAME:\t\t' + str(self.players[player]['name']))
            print('HAND:\t\t' + (str(hand[0].get_rank()) + ' ' + str(hand[0].get_suit()) + ', '
                  + str(hand[1].get_rank()) + ' ' + str(hand[1].get_suit()) if len(hand) > 0 else str(hand)))
            print('CURRENT_BET:\t' + str(self.players[player]['current_bet']))
            print('CURRENT_MOVE:\t' + str(self.players[player]['current_move']))
            print('CURRENT_CHIPS:\t' + str(player.get_amount_of_chips()))
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
        print('HIGHEST_BETTER:\t' + (str(self.highest_better) if self.highest_better is None
              else str(self.players[self.highest_better]['name'])))
        print('CURRENT_BET:\t' + str(self.current_bet))
        print('CURRENT_RAISE:\t' + str(self.current_raise))
        print('RAISE_CNT:\t' + str(self.raise_cnt))
        print('COMMUNITY_CARDS:' + cards)
        print()

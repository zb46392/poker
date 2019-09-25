from . import Deck
from . import Player


INIT_CHIPS = 100


class Game:
    def __init__(self, num_of_players):
        if num_of_players < 2:
            raise ValueError('At least 2 players')

        self.deck = Deck()
        self.players = list()
        self.pot = 0
        self.dealer_id = 0

        for i in range(num_of_players):
            self.players.append(Player(INIT_CHIPS))

    def init_preflop_phase(self):
        pass
        '''
        collect blinds
        player action ( call, fold or raise )
        '''

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

    '''
    SPECIAL CASES:
     - all players fold besides one -> skip remaining phases send pot to remaining player
     - all in ( player has not enough to call but calls ) -> split pot
    '''

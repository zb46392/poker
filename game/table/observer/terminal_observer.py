from . import BaseObserver, State


class TerminalObserver(BaseObserver):
    def update(self, state: State) -> None:
        print('-------------' + str(state.phase) + '-------------')
        print(' POT:\t' + str(state.pot) + '')
        print(' CARDS:\t' + str(state.community_cards))
        print(' PLAYERS:')
        print()
        for player in state.players:
            print('   NAME:\t' + player.name)
            print('   HAND:\t' + str(player.basic_player.get_hand()))
            print('   CHIPS:\t' + str(player.basic_player.get_amount_of_chips()))
            print('   MOVE:\t' + str(player.current_move))
            print('   BET:\t' + str(player.current_bet))
            print('   FINAL:\t' + str(player.final_hand) + '\t' + str(player.final_hand_type))
            print('   SCORE:\t' + str(player.score))
            print()
        print()

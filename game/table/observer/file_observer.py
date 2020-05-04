from . import BaseObserver, State
from datetime import datetime
from os.path import join as path_join


class FileObserver(BaseObserver):
    def __init__(self, directory_path: str) -> None:
        super().__init__()
        self._datetime = datetime.now()
        self._dir_path = directory_path
        self._log_name = ''.join(str(self._datetime.timestamp()).split('.')) + '.log'
        self._log_path = path_join(self._dir_path, self._log_name)

        with open(self._log_path, 'w') as file:
            file.write('POKER GAME: ' + str(self._datetime.isoformat()) + '\n')

    # TO_DO
    # GENERATE LOG DIR PATH & CREATE LOG FOLDER IF DOESN'T EXISTS
    # PRINT WINNER AT END OF GAME -> GET BOT CLASS NAMES

    def update(self, state: State) -> None:
        with open(self._log_path, 'a') as file:
            file.write('-------------' + str(state.phase) + '-------------\n')
            file.write(' POT:\t' + str(state.pot) + '\n')
            file.write(' CARDS:\t' + str(state.community_cards) + '\n')
            file.write(' PLAYERS:\n')
            file.write('\n')
            for player in state.players:
                file.write('   NAME:\t' + player.name + '\n')
                file.write('   HAND:\t' + str(player.get_hand()) + '\n')
                file.write('   CHIPS:\t' + str(player.get_amount_of_chips()) + '\n')
                file.write('   MOVE:\t' + str(player.current_move) + '\n')
                file.write('   BET:\t\t' + str(player.current_bet) + '\n')
                file.write('   FINAL:\t' + str(player.final_hand) + '\t' + str(player.final_hand_type) + '\n')
                file.write('   SCORE:\t' + str(player.score) + '\n')
                file.write('\n')
            file.write('\n')

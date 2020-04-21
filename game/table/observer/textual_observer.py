from . import BaseObserver, State
from abc import ABC, abstractmethod
from game import Phases


class TextualObserver(BaseObserver, ABC):

    def update(self, state: State) -> None:
        self._apply_new_msg(self._generate_info_msg(state))

    @staticmethod
    def _generate_info_msg(state: State) -> str:
        info_msg = ''

        info_msg += f'-------------{str(state.phase)}-------------\n'
        info_msg += f' POT:\t{str(state.pot)}\n'
        info_msg += f' CARDS:\t{str(state.community_cards)}\n'
        info_msg += ' PLAYERS:\n'
        info_msg += '\n'
        for player in state.players:
            info_msg += f'   NAME:\t{player.name}\n'
            info_msg += f'   HAND:\t{str(player.get_hand())}\n'
            info_msg += f'   CHIPS:\t{str(player.get_amount_of_chips())}\n'
            info_msg += f'   MOVE:\t{str(player.current_move)}\n'
            info_msg += f'   BET:\t\t{str(player.current_bet)}\n'
            info_msg += f'   FINAL:\t{str(player.final_hand)}\t{str(player.final_hand_type)}\n'
            info_msg += f'   SCORE:\t{str(player.score)}\n'
            info_msg += '\n'
        info_msg += '\n'

        if state.phase is Phases.SHOWDOWN:
            info_msg += ' POT COLLECTIONS\n'
            for player in state.individual_pot_collection:
                info_msg += f'   {player.name}:\t{state.individual_pot_collection.get(player)}\n'

        return info_msg

    @abstractmethod
    def _apply_new_msg(self, msg: str) -> None:
        pass

from .. import BaseObserver as RootBaseObserver, State
from abc import ABC, abstractmethod
from game import Phases


class Base(RootBaseObserver, ABC):
    def __init__(self) -> None:
        super().__init__()
        self._info = ''
        self._phase = ''
        self._state = ''
        self._pot_collection = ''
        self._is_pot_collection = False

    def update(self, state: State) -> None:
        self._acquire_information(state)
        self._apply_new_info()

    def _acquire_information(self, state: State) -> None:
        self._acquire_phase_information(state)
        self._acquire_state_information(state)
        self._acquire_pot_collection_information(state)

        self._info = self._phase + self._state + self._pot_collection

    @abstractmethod
    def _apply_new_info(self) -> None:
        pass

    def _acquire_phase_information(self, state: State) -> None:
        self._phase = f'-------------{str(state.phase)}-------------\n'

    def _acquire_state_information(self, state: State) -> None:
        state_info = ''
        state_info += f' POT:\t{str(state.pot)}\n'
        state_info += f' CARDS:\t{str(state.community_cards)}\n'
        state_info += ' PLAYERS:\n'
        state_info += '\n'
        for player in state.players:
            state_info += f'   NAME:\t{player.name}\n'
            state_info += f'   HAND:\t{str(player.get_hand())}\n'
            state_info += f'   CHIPS:\t{str(player.get_amount_of_chips())}\n'
            state_info += f'   MOVE:\t{str(player.current_move)}\n'
            state_info += f'   BET:\t\t{str(player.current_bet)}\n'
            state_info += f'   FINAL:\t{str(player.final_hand)}\t{str(player.final_hand_type)}\n'
            state_info += f'   SCORE:\t{str(player.score)}\n'
            state_info += '\n'
        state_info += '\n'

        self._state = state_info

    def _acquire_pot_collection_information(self, state: State) -> None:
        pot_collection_info = ''
        self._is_pot_collection = state.phase is Phases.POT_COLLECTION

        if self._is_pot_collection:

            pot_collection_info += ' POT COLLECTIONS\n'
            for player in state.individual_pot_collection:
                pot_collection_info += f'   {player.name}:\t{state.individual_pot_collection.get(player)}\n'

        self._pot_collection = pot_collection_info

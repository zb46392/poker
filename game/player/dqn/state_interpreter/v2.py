from .base import Base
from game.player.dqn.state_interpreter import InterpretableState
from game.moves import Moves
from game.final_hand import FinalHandType, StrongestFinalHandFinder
from typing import List, Tuple


class V2(Base):

    @property
    def state_space(self) -> int:
        # CARDS IN HAND:    52
        # CARDS ON TABLE:   52
        # ALLOWED ACTIONS:   5
        # HAND TYPE:        10
        # --------------------
        # TOTAL:           119

        return 119

    def _generate_interpreted_state(self, state: InterpretableState) -> List[float]:
        hand, community_cards = self._generate_cards_states_parts(state)
        allowed_actions = self._generate_allowed_actions_state_part(state)
        hand_type = self._generate_hand_type_state_part(state)

        return hand + community_cards + allowed_actions + hand_type

    def _generate_cards_states_parts(self, state: InterpretableState) -> Tuple[List[float], List[float]]:
        hand_state_part = []
        community_cards_state_part = []

        for card in self._deck.get_cards():
            if card in state.hand:
                hand_state_part.append(1.0)
            else:
                hand_state_part.append(0.0)

            if card in state.game_state.community_cards:
                community_cards_state_part.append(1.0)
            else:
                community_cards_state_part.append(0.0)

        return hand_state_part, community_cards_state_part

    @staticmethod
    def _generate_allowed_actions_state_part(state: InterpretableState) -> List[float]:
        allowed_actions_state_part = []

        for move in Moves:
            if move in state.game_state.allowed_moves:
                allowed_actions_state_part.append(1.0)
            else:
                allowed_actions_state_part.append(0.0)

        return allowed_actions_state_part

    @staticmethod
    def _generate_hand_type_state_part(state: InterpretableState) -> List[float]:
        hand_type_state_part = []

        final_hand = StrongestFinalHandFinder.find(list(state.hand + state.game_state.community_cards))

        for t in FinalHandType:
            if final_hand.type is t:
                hand_type_state_part.append(1.0)
            else:
                hand_type_state_part.append(0.0)

        return hand_type_state_part

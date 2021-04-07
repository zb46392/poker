from .base import Base
from . import InterpretableState
from game.final_hand import FinalHandType, StrongestFinalHandFinder
from typing import List


class V0(Base):

    @property
    def state_space(self) -> int:
        # HAND TYPES:           10
        # CHIPS:                30
        # IS RAISING CAPPED:     1
        # -------------------------
        # TOTAL:                41
        return 41

    def _generate_interpreted_state(self, state: InterpretableState) -> List[float]:
        cards = self._generate_card_state_part(state)
        chips = self._generate_chips_state_part(state)
        is_raising_capped = self._generate_is_raising_capped_state_part(state)

        return cards + chips + is_raising_capped

    @staticmethod
    def _generate_card_state_part(state: InterpretableState) -> List[float]:
        cards_state_part = []

        final_hand = StrongestFinalHandFinder.find(list(state.hand + state.game_state.community_cards))

        for t in FinalHandType:
            if final_hand.type is t:
                cards_state_part.append(1.0)
            else:
                cards_state_part.append(0.0)

        return cards_state_part

    @staticmethod
    def _generate_chips_state_part(state: InterpretableState) -> List[float]:
        chips_state_part = []

        for i in range(state.game_state.total_chips):
            if i == (state.current_chips_amount - 1):
                chips_state_part.insert(0, 1.0)
            else:
                chips_state_part.insert(0, 0.0)

        return chips_state_part

    @staticmethod
    def _generate_is_raising_capped_state_part(state: InterpretableState) -> List[float]:
        if state.game_state.is_raising_capped:
            return [1.0]
        else:
            return [0.0]

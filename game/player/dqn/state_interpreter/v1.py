from .base import Base
from . import InterpretableState
from typing import List


class V1(Base):

    @property
    def state_space(self) -> int:
        # CARDS:                52
        # CHIPS:                30
        # IS RAISING CAPPED:     1
        # -------------------------
        # TOTAL:                83
        return 83

    def _generate_interpreted_state(self, state: InterpretableState) -> List[float]:
        cards = self._generate_card_state_part(state)
        chips = self._generate_chips_state_part(state)
        is_raising_capped = self._generate_is_raising_capped_state_part(state)

        return cards + chips + is_raising_capped

    def _generate_card_state_part(self, state: InterpretableState) -> List[float]:
        cards_state_part = []

        for card in self._deck.get_cards():
            if card in state.hand or card in state.game_state.community_cards:
                cards_state_part.append(1.0)
            else:
                cards_state_part.append(0.0)

        return cards_state_part

    @staticmethod
    def _generate_chips_state_part(state: InterpretableState) -> List[float]:
        total_chips = state.game_state.total_chips
        remaining_chips = total_chips - state.current_chips_amount

        chips_state_part = []

        for _ in range(remaining_chips):
            chips_state_part.append(0.0)

        for _ in range(state.current_chips_amount):
            chips_state_part.append(1.0)

        return chips_state_part

    @staticmethod
    def _generate_is_raising_capped_state_part(state: InterpretableState) -> List[float]:
        if state.game_state.is_raising_capped:
            return [1.0]
        else:
            return [0.0]

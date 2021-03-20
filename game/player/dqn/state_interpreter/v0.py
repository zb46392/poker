from .base import Base
from game.state import State
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

    @property
    def total_chips_amount(self) -> int:
        return self._total_chips_amount

    def _generate_interpreted_state(self, state: State) -> List[float]:
        cards = self._generate_card_state_part(state)
        chips = self._generate_chips_state_part()
        is_raising_capped = self._generate_is_raising_capped_state_part(state)

        return cards + chips + is_raising_capped

    def _generate_card_state_part(self, state: State) -> List[float]:
        cards_state_part = []

        final_hand = StrongestFinalHandFinder.find(self._player.get_hand() + list(state.community_cards))

        for t in FinalHandType:
            if final_hand.type is t:
                cards_state_part.append(1.0)
            else:
                cards_state_part.append(0.0)

        return cards_state_part

    def _generate_chips_state_part(self) -> List[float]:
        chips_state_part = []

        for i in range(self._total_chips_amount):
            if i == (self._player.get_amount_of_chips() - 1):
                chips_state_part.insert(0, 1.0)
            else:
                chips_state_part.insert(0, 0.0)

        return chips_state_part

    @staticmethod
    def _generate_is_raising_capped_state_part(state: State) -> List[float]:
        if state.is_raising_capped:
            return [1.0]
        else:
            return [0.0]

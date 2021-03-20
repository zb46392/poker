from .base import Base
from game.state import State
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

    def _generate_interpreted_state(self, state: State) -> List[float]:
        cards = self._generate_card_state_part(state)
        chips = self._generate_chips_state_part()
        is_raising_capped = self._generate_is_raising_capped_state_part(state)

        return cards + chips + is_raising_capped

    def _generate_card_state_part(self, state: State) -> List[float]:
        cards_state_part = []
        hand = self._player.get_hand()

        for card in self._deck.get_cards():
            if card in hand or card in state.community_cards:
                cards_state_part.append(1.0)
            else:
                cards_state_part.append(0.0)

        return cards_state_part

    def _generate_chips_state_part(self) -> List[float]:
        owning_chips = self._player.get_amount_of_chips()
        remaining_chips = self._total_chips_amount - owning_chips

        chips_state_part = []

        for _ in range(remaining_chips):
            chips_state_part.append(0.0)

        for _ in range(owning_chips):
            chips_state_part.append(1.0)

        return chips_state_part

    @staticmethod
    def _generate_is_raising_capped_state_part(state: State) -> List[float]:
        if state.is_raising_capped:
            return [1.0]
        else:
            return [0.0]

from game import Card, Deck, Moves, State
from typing import List


class StateInterpreter:
    def __init__(self, chips: int) -> None:
        self._starting_chips_amount = chips
        self._total_chips_amount = None
        self._deck = Deck()

    @property
    def state_space(self) -> int:
        return 83

    @property
    def action_space(self) -> int:
        return len(Moves)

    @property
    def total_chips_amount(self) -> int:
        return self._total_chips_amount

    def interpret(self, hand: List[Card], state: State, chips: int) -> List[float]:
        if self._total_chips_amount is None:
            self._determine_total_chips_amount(state)

        cards = self._generate_card_state_part(hand, state)
        chips = self._generate_chips_state_part(chips)
        is_raising_capped = self._generate_is_raising_capped_state_part(state)

        return cards + chips + is_raising_capped

    def _determine_total_chips_amount(self, state: State) -> None:
        self._total_chips_amount = state.total_nbr_of_players * self._starting_chips_amount

    def _generate_card_state_part(self, hand: List[Card], state: State) -> List[float]:
        cards_state_part = []

        for card in self._deck.get_cards():
            if card in hand or card in state.community_cards:
                cards_state_part.append(1.0)
            else:
                cards_state_part.append(0.0)

        return cards_state_part

    def _generate_chips_state_part(self, owning_chips: int) -> List[float]:
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

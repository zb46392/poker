from . import FinalHandType, FinalHand
from game import Card
from typing import Dict, List, Optional


class StrongestFinalHandFinder:
    @staticmethod
    def find(cards: List[Card]) -> FinalHand:
        hand = sorted(cards, reverse=True)
        final_hand = StrongestFinalHandFinder._try_find_flush(hand)

        if final_hand is not None:
            bigger_hand = StrongestFinalHandFinder._try_find_straight(final_hand)
            if bigger_hand is not None:
                if StrongestFinalHandFinder._is_royal_flush(bigger_hand):
                    return StrongestFinalHandFinder._create_final_hand(bigger_hand, FinalHandType.ROYAL_FLUSH)
                else:
                    return StrongestFinalHandFinder._create_final_hand(bigger_hand, FinalHandType.STRAIGHT_FLUSH)
            else:
                return StrongestFinalHandFinder._create_final_hand(final_hand, FinalHandType.FLUSH)

        final_hand = StrongestFinalHandFinder._try_find_poker(hand)
        if final_hand is not None:
            return StrongestFinalHandFinder._create_final_hand(final_hand, FinalHandType.POKER)

        final_hand = StrongestFinalHandFinder._try_find_full_house(hand)
        if final_hand is not None:
            return StrongestFinalHandFinder._create_final_hand(final_hand, FinalHandType.FULL_HOUSE)

        final_hand = StrongestFinalHandFinder._try_find_straight(hand)
        if final_hand is not None:
            return StrongestFinalHandFinder._create_final_hand(final_hand, FinalHandType.STRAIGHT)

        final_hand = StrongestFinalHandFinder._try_find_tris(hand)
        if final_hand is not None:
            return StrongestFinalHandFinder._create_final_hand(final_hand, FinalHandType.TRIS)

        final_hand = StrongestFinalHandFinder._try_find_two_pair(hand)
        if final_hand is not None:
            return StrongestFinalHandFinder._create_final_hand(final_hand, FinalHandType.TWO_PAIRS)

        final_hand = StrongestFinalHandFinder._try_find_pair(hand)
        if final_hand is not None:
            return StrongestFinalHandFinder._create_final_hand(final_hand, FinalHandType.PAIR)

        return StrongestFinalHandFinder._create_final_hand(hand[:5], FinalHandType.HIGH_CARD)

    @staticmethod
    def find_stronger_hand(final_hand1: FinalHand, final_hand2: FinalHand) -> Optional[FinalHand]:
        if final_hand1.score == final_hand2.score:
            hand1 = sorted(final_hand1.hand, reverse=True)
            hand2 = sorted(final_hand2.hand, reverse=True)

            nbr_of_cards = len(hand1) if len(hand1) < len(hand2) else len(hand2)

            for i in range(nbr_of_cards):
                if hand1[i].value > hand2[i].value:
                    return final_hand1

                if hand2[i].value > hand1[i].value:
                    return final_hand2

            return None

        elif final_hand1.score > final_hand2.score:
            return final_hand1

        else:
            return final_hand2

    @staticmethod
    def _create_final_hand(hand: List[Card], hand_type: FinalHandType) -> FinalHand:
        if hand_type is FinalHandType.TWO_PAIRS or hand_type is FinalHandType.FULL_HOUSE:
            score = hand[0].value * hand_type.value + hand[3].value
        else:
            score = hand[0].value * hand_type.value

        return FinalHand(hand=hand, type=hand_type, score=score)

    @staticmethod
    def _try_find_flush(sorted_cards: List[Card]) -> Optional[List[Card]]:
        suits = dict()

        for card in sorted_cards:
            if card.suit not in suits:
                suits[card.suit] = list()

            suits[card.suit].append(card)

        for suit in suits:
            if len(suits[suit]) >= 5:
                return suits[suit][:5]

        return None

    @staticmethod
    def _try_find_straight(sorted_cards: List[Card]) -> Optional[List[Card]]:
        cnt = 0
        previous_card = sorted_cards[0]

        for i in range(1, len(sorted_cards)):
            if sorted_cards[i].value != previous_card.value - 1:
                cnt = 0
            else:
                cnt += 1
                if cnt == 4:
                    return sorted_cards[i - 4:i + 1]

            previous_card = sorted_cards[i]

        if cnt == 3 and sorted_cards[0].value == 13 and sorted_cards[-1].value == 1:
            return sorted_cards[len(sorted_cards) - 4:-1] + [sorted_cards[0]]

        return None

    @staticmethod
    def _is_royal_flush(cards: List[Card]) -> bool:
        return (cards[0].value == 13
                and cards[1].value == 12
                and cards[2].value == 11
                and cards[3].value == 10
                and cards[4].value == 9
                and cards[0].suit
                == cards[1].suit
                == cards[2].suit
                == cards[3].suit
                == cards[4].suit)

    @staticmethod
    def _try_find_poker(sorted_cards: List[Card]) -> Optional[List[Card]]:
        same_value_cards = StrongestFinalHandFinder._find_same_value_cards(sorted_cards, 4)

        if same_value_cards is not None:
            high_value_card = StrongestFinalHandFinder._find_high_value_cards_not_in_cards(
                same_value_cards, sorted_cards, 1)
            return same_value_cards + high_value_card

        return None

    @staticmethod
    def _find_same_value_cards(cards: List[Card], amount: int) -> Optional[List[Card]]:
        cards_by_value = StrongestFinalHandFinder._divide_cards_by_value(cards)

        for same_value_cards in cards_by_value:
            if len(cards_by_value[same_value_cards]) >= amount:
                return cards_by_value[same_value_cards][:amount]

        return None

    @staticmethod
    def _divide_cards_by_value(cards: List[Card]) -> Dict[int, List[Card]]:
        same_value_cards = dict()

        for card in cards:
            if card.value not in same_value_cards:
                same_value_cards[card.value] = list()

            same_value_cards[card.value].append(card)

        return same_value_cards

    @staticmethod
    def _find_high_value_cards_not_in_cards(selected_cards: List[Card], cards: List[Card], amount: int) -> List[Card]:
        high_value_cards = list()
        for card in cards:
            if card not in selected_cards:
                high_value_cards.append(card)
                if len(high_value_cards) == amount:
                    break
        return high_value_cards

    @staticmethod
    def _try_find_full_house(sorted_cards: List[Card]) -> Optional[List[Card]]:
        same_3_cards = StrongestFinalHandFinder._find_same_value_cards(sorted_cards, 3)

        if same_3_cards is not None:
            same_2_cards = StrongestFinalHandFinder._find_same_value_cards(
                [card for card in sorted_cards if card not in same_3_cards], 2)

            if same_2_cards is not None:
                return same_3_cards + same_2_cards

        return None

    @staticmethod
    def _try_find_tris(sorted_cards: List[Card]) -> Optional[List[Card]]:
        same_value_cards = StrongestFinalHandFinder._find_same_value_cards(sorted_cards, 3)

        if same_value_cards is not None:
            high_value_cards = StrongestFinalHandFinder._find_high_value_cards_not_in_cards(
                same_value_cards, sorted_cards, 2)
            return same_value_cards + high_value_cards

        return None

    @staticmethod
    def _try_find_two_pair(sorted_cards: List[Card]) -> Optional[List[Card]]:
        first_pair = StrongestFinalHandFinder._find_same_value_cards(sorted_cards, 2)

        if first_pair is not None:
            second_pair = StrongestFinalHandFinder._find_same_value_cards(
                [card for card in sorted_cards if card not in first_pair], 2)

            if second_pair is not None:
                high_value_cards = StrongestFinalHandFinder._find_high_value_cards_not_in_cards(
                    first_pair + second_pair, sorted_cards, 1)
                return first_pair + second_pair + high_value_cards

        return None

    @staticmethod
    def _try_find_pair(sorted_cards: List[Card]) -> Optional[List[Card]]:
        same_value_cards = StrongestFinalHandFinder._find_same_value_cards(sorted_cards, 2)

        if same_value_cards is not None:
            high_value_cards = StrongestFinalHandFinder._find_high_value_cards_not_in_cards(
                same_value_cards, sorted_cards, 3)
            return same_value_cards + high_value_cards

        return None

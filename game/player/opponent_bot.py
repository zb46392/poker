from . import Player
from .. import Moves, State
from game import Card, Deck, Phases, StrongestFinalHandFinder
from random import randint
from typing import List, Tuple, Optional


class OpponentBot(Player):
    """
    Bot is based on paper:
                                Opponent Modeling in Poker
                                            by
                    Darse Billings, Denis Papp, Jonathan Schaeffer, Duane Szafron
    (http://www.cs.virginia.edu/~evans/poker/wp-content/uploads/2011/02/opponent_modeling_in_poker_billings.pdf)
    """
    FOLD_THRESH = 50
    RAISE_THRESH = 50
    BLUFF_THRESH = 50

    def __init__(self, chips: int, name: Optional[str] = None,
                 fold_thresh: Optional[int] = None,
                 raise_thresh: Optional[int] = None,
                 bluff_thresh: Optional[int] = None):
        """
        The lower the threshold the greater the probability for action to take.

        :param fold_thresh: threshold for folding (on raise) - Between 1 and 100
        :param raise_thresh: threshold for raising - Between 1 and 100
        :param bluff_thresh: threshold for call/raise (bluffing) - Between 1 and 100
        """
        super().__init__(chips, name)
        if fold_thresh is None:
            fold_thresh = OpponentBot.FOLD_THRESH

        if raise_thresh is None:
            raise_thresh = OpponentBot.RAISE_THRESH

        if bluff_thresh is None:
            bluff_thresh = OpponentBot.BLUFF_THRESH

        self._fold_thresh = fold_thresh
        self._raise_thresh = raise_thresh
        self._bluff_thresh = bluff_thresh

    @property
    def fold_thresh(self) -> int:
        return self._fold_thresh

    @fold_thresh.setter
    def fold_thresh(self, thresh: int) -> None:
        self._fold_thresh = thresh

    @property
    def raise_thresh(self) -> int:
        return self._raise_thresh

    @raise_thresh.setter
    def raise_thresh(self, thresh: int) -> None:
        self._raise_thresh = thresh

    @property
    def bluff_thresh(self) -> int:
        return self._bluff_thresh

    @bluff_thresh.setter
    def bluff_thresh(self, thresh: int) -> None:
        self._bluff_thresh = thresh

    @staticmethod
    def _generate_ehs_description() -> str:
        return """
        The algorithm is a numerical approach to quantify the strength of a poker hand where its 
        result expresses the strength of a particular hand in percentile (i.e. ranging from 0 to 1), 
        compared to all other possible hands.

        EHS = HS * (1 - NPOT) + (1 - HS) * PPOT

        where:
         - EHS:     Effective Hand Strength
         - HS:      Is the current Hand Strength (i.e. not taking into account potential to improve or deteriorate, 
                    depending on upcoming table cards
         - NPOT:    Is the Negative POTential (i.e. the probability that our current hand, 
                    if the strongest, deteriorates and becomes a losing hand)
         - PPOT:    Is the Positive POTential (i.e. the probability that our current hand, 
                    if losing, improves and becomes the winning hand)
        """

    def make_move(self, possible_moves: List[Moves], game_state: State) -> Moves:
        """
        On pre-flop make decision based on card group (see _calculate_pre_flop_hand_strength function).
        Flop, turn, river make decision based just by hand strength,
        effective hand strength is computationally to intensive.

        :param possible_moves:
        :param game_state:
        :return: Move to be executed...
        """

        if game_state.current_phase is Phases.PRE_FLOP:
            hand_strength = self._calculate_pre_flop_hand_strength()
        else:
            hand_strength = self._calculate_post_pre_flop_hand_strength(game_state)

        feeling_lucky = randint(1, 100)

        current_move = possible_moves[0]

        if Moves.ALL_IN in possible_moves:
            current_move = Moves.ALL_IN
        elif Moves.RAISE in possible_moves and Moves.CHECK in possible_moves:
            if hand_strength >= self._raise_thresh or feeling_lucky >= self._bluff_thresh:
                current_move = Moves.RAISE
            else:
                current_move = Moves.CHECK
        elif Moves.CALL in possible_moves:
            if Moves.RAISE in possible_moves \
                    and hand_strength >= self._fold_thresh \
                    and feeling_lucky >= self._bluff_thresh:
                current_move = Moves.RAISE
            elif hand_strength >= self._fold_thresh or feeling_lucky >= self._bluff_thresh:
                current_move = Moves.CALL
            else:
                current_move = Moves.FOLD
        elif Moves.CHECK in possible_moves:
            current_move = Moves.CHECK

        return current_move

    def _calculate_pre_flop_hand_strength(self) -> int:
        """
        Strength calculation based on the Sklansky & Malmuth starting hands table.
        https://www.thepokerbank.com/strategy/basic/starting-hand-selection/sklansky-groups/

        1 	AA, AKs, KK, QQ, JJ
        2 	AK, AQs, AJs, KQs, TT
        3 	AQ, ATs, KJs, QJs, JTs, 99
        4 	AJ, KQ, KTs, QTs, J9s, T9s, 98s, 88
        5 	A9s - A2s, KJ, QJ, JT, Q9s, T8s, 97s, 87s, 77, 76s, 66
        6 	AT, KT, QT, J8s, 86s, 75s, 65s, 55, 54s
        7 	K9s - K2s, J9, T9, 98, 64s, 53s, 44, 43s, 33, 22
        8 	A9, K9, Q9, J8, J7s, T8, 96s, 87, 85s, 76, 74s, 65, 54, 42s, 32s
        9 	All other hands not required above.

        :param game_state:
        :return: Hand strength
        """
        if self._is_hand_in_1_st_group():
            return 100
        elif self._is_hand_in_2_nd_group():
            return 88
        elif self._is_hand_in_3_rd_group():
            return 77
        elif self._is_hand_in_4_th_group():
            return 66
        elif self._is_hand_in_5_th_group():
            return 55
        elif self._is_hand_in_6_th_group():
            return 44
        elif self._is_hand_in_7_th_group():
            return 33
        elif self._is_hand_in_8_th_group():
            return 22
        else:
            return 11

    def _calculate_post_pre_flop_hand_strength(self, state: State) -> int:
        hs = self.calculate_hand_strength(state)
        return int(round(hs * 100))

    def _is_hand_in_1_st_group(self) -> bool:
        """
        AA, AKs, KK, QQ, JJ
        :return: BOOL
        """

        c1, c2 = sorted(self.get_hand(), reverse=True)

        return (
                (c1.rank == 'Ace' and c2.rank == 'Ace')
                or (c1.rank == 'Ace' and c2.rank == 'King' and c1.suit == c2.suit)
                or (c1.rank == 'King' and c2.rank == 'King')
                or (c1.rank == 'Queen' and c2.rank == 'Queen')
                or (c1.rank == 'Jack' and c2.rank == 'Jack')
        )

    def _is_hand_in_2_nd_group(self) -> bool:
        """
        AK, AQs, AJs, KQs, TT
        :return: BOOL
        """

        c1, c2 = sorted(self.get_hand(), reverse=True)

        return (
                (c1.rank == 'Ace' and c2.rank == 'King')
                or (c1.rank == 'Ace' and c1.rank == 'Queen' and c1.suit == c2.suit)
                or (c1.rank == 'Ace' and c2.rank == 'Jack' and c1.suit == c2.suit)
                or (c1.rank == 'King' and c2.rank == 'Queen' and c1.suit == c2.suit)
                or (c1.rank == '10' and c2.rank == '10')
        )

    def _is_hand_in_3_rd_group(self) -> bool:
        """
        AQ, ATs, KJs, QJs, JTs, 99
        :return: BOOL
        """
        c1, c2 = sorted(self.get_hand(), reverse=True)

        return (
                (c1.rank == 'Ace' and c2.rank == 'Queen')
                or (c1.rank == 'Ace' and c2.rank == '10' and c1.suit == c2.suit)
                or (c1.rank == 'King' and c2.rank == 'Jack' and c1.suit == c2.suit)
                or (c1.rank == 'Queen' and c2.rank == 'Jack' and c1.suit == c2.suit)
                or (c1.rank == 'Jack' and c2.rank == '10' and c1.suit == c2.suit)
                or (c1.rank == '9' and c2.rank == '9')
        )

    def _is_hand_in_4_th_group(self) -> bool:
        """
        AJ, KQ, KTs, QTs, J9s, T9s, 98s, 88
        :return: BOOL
        """

        c1, c2 = sorted(self.get_hand(), reverse=True)

        return (
                (c1.rank == 'Ace' and c2.rank == 'Jack')
                or (c1.rank == 'King' and c2.rank == 'Queen')
                or (c1.rank == 'King' and c2.rank == '10' and c1.suit == c2.suit)
                or (c1.rank == 'Queen' and c2.rank == '10' and c1.suit == c2.suit)
                or (c1.rank == 'Jack' and c2.rank == '9' and c1.suit == c2.suit)
                or (c1.rank == '10' and c2.rank == '9' and c1.suit == c2.suit)
                or (c1.rank == '9' and c2.rank == '8' and c1.suit == c2.suit)
                or (c1.rank == '8' and c2.rank == '8')

        )

    def _is_hand_in_5_th_group(self) -> bool:
        """
        A9s - A2s, KJ, QJ, JT, Q9s, T8s, 97s, 87s, 77, 76s, 66
        :return: BOOL
        """

        c1, c2 = sorted(self.get_hand(), reverse=True)
        return (
                (c1.rank == 'Ace' and c2.value < 9 and c1.suit == c2.suit)
                or (c1.rank == 'King' and c2.rank == 'Jack')
                or (c1.rank == 'Queen' and c2.rank == 'Jack')
                or (c1.rank == 'Jack' and c2.rank == '10')
                or (c1.rank == 'Queen' and c2.rank == '9' and c1.suit == c2.suit)
                or (c1.rank == '10' and c2.rank == '8' and c1.suit == c2.suit)
                or (c1.rank == '9' and c2.rank == '7' and c1.suit == c2.suit)
                or (c1.rank == '8' and c2.rank == '7' and c1.suit == c2.suit)
                or (c1.rank == '7' and c2.rank == '7')
                or (c1.rank == '7' and c2.rank == '6' and c1.suit == c2.suit)
                or (c1.rank == '6' and c2.rank == '6')
        )

    def _is_hand_in_6_th_group(self) -> bool:
        """
        AT, KT, QT, J8s, 86s, 75s, 65s, 55, 54s
        :return: BOOL
        """

        c1, c2 = sorted(self.get_hand(), reverse=True)
        return (
                (c1.rank == 'Ace' and c2.rank == '10')
                or (c1.rank == 'King' and c2.rank == '10')
                or (c1.rank == 'Queen' and c2.rank == '10')
                or (c1.rank == 'Jack' and c2.rank == '8' and c1.suit == c2.suit)
                or (c1.rank == '8' and c2.rank == '6' and c1.suit == c2.suit)
                or (c1.rank == '7' and c2.rank == '5' and c1.suit == c2.suit)
                or (c1.rank == '6' and c2.rank == '5' and c1.suit == c2.suit)
                or (c1.rank == '5' and c2.rank == '5')
                or (c1.rank == '5' and c2.rank == '4' and c1.suit == c2.suit)
        )

    def _is_hand_in_7_th_group(self) -> bool:
        """
        K9s - K2s, J9, T9, 98, 64s, 53s, 44, 43s, 33, 22
        :return: BOOL
        """

        c1, c2 = sorted(self.get_hand(), reverse=True)
        return (
                (c1.rank == 'King' and c2.value < 9 and c1.suit == c2.suit)
                or (c1.rank == 'Jack' and c2.rank == '9')
                or (c1.rank == '10' and c2.rank == '9')
                or (c1.rank == '9' and c2.rank == '8')
                or (c1.rank == '6' and c2.rank == '4' and c1.suit == c2.suit)
                or (c1.rank == '5' and c2.rank == '3' and c1.suit == c2.suit)
                or (c1.rank == '4' and c2.rank == '4')
                or (c1.rank == '4' and c2.rank == '3' and c1.suit == c2.suit)
                or (c1.rank == '3' and c2.rank == '3')
                or (c1.rank == '2' and c2.rank == '2')
        )

    def _is_hand_in_8_th_group(self) -> bool:
        """
        A9, K9, Q9, J8, J7s, T8, 96s, 87, 85s, 76, 74s, 65, 54, 42s, 32s
        :return: BOOL
        """

        c1, c2 = sorted(self.get_hand(), reverse=True)
        return (
                (c1.rank == 'Ace' and c2.rank == '9')
                or (c1.rank == 'King' and c2.rank == '9')
                or (c1.rank == 'Queen' and c2.rank == '9')
                or (c1.rank == 'Jack' and c2.rank == '7' and c1.suit == c2.suit)
                or (c1.rank == '10' and c2.rank == '8')
                or (c1.rank == '9' and c2.rank == '6' and c1.suit == c2.suit)
                or (c1.rank == '8' and c2.rank == '7')
                or (c1.rank == '8' and c2.rank == '5' and c1.suit == c2.suit)
                or (c1.rank == '7' and c2.rank == '6')
                or (c1.rank == '7' and c2.rank == '4' and c1.suit == c2.suit)
                or (c1.rank == '6' and c2.rank == '5')
                or (c1.rank == '5' and c2.rank == '4')
                or (c1.rank == '4' and c2.rank == '2' and c1.suit == c2.suit)
                or (c1.rank == '3' and c2.rank == '2' and c1.suit == c2.suit)
        )

    def calculate_ehs(self, state: State) -> float:
        f"""
        {self._generate_ehs_description()}
        :param state:
        :return: EFS (effective hand strength) in percentile
        """

        hs, npot, ppot = self._calculate_hand_strength_potential(state)

        return hs * (1 - npot) + (1 - hs) * ppot

    def calculate_hand_strength(self, state: State) -> float:
        ahead = tied = behind = 0
        my_final_hand = StrongestFinalHandFinder.find(self.get_hand() + list(state.community_cards))

        for opp_hand in self._create_opponent_hand_combinations(state):
            opp_final_hand = StrongestFinalHandFinder.find(list(opp_hand) + list(state.community_cards))

            stronger_hand = StrongestFinalHandFinder.find_stronger_hand(my_final_hand, opp_final_hand)

            if my_final_hand is stronger_hand:
                ahead += 1
            elif opp_final_hand is stronger_hand:
                behind += 1
            else:
                tied += 1

        hand_strength = (ahead + tied / 2) / (ahead + tied + behind)

        return hand_strength

    def _calculate_hand_strength_potential(self, state: State) -> Tuple[float, float, float]:
        """
        Currently not usable for 2 reasons:
        1) Return number range not between 0 and 1
        2) Computationally to intensive
        :param state:
        :return:
        """
        hand_potential = {
            'ahead': {'ahead': 0, 'behind': 0, 'tied': 0},
            'behind': {'ahead': 0, 'behind': 0, 'tied': 0},
            'tied': {'ahead': 0, 'behind': 0, 'tied': 0}
        }
        total_hand_potential = {'ahead': 0, 'behind': 0, 'tied': 0}

        my_final_hand = StrongestFinalHandFinder.find(self.get_hand() + list(state.community_cards))

        opp_hand_combos = self._create_opponent_hand_combinations(state)

        for opp_combo in opp_hand_combos:
            opp_final_hand = StrongestFinalHandFinder.find(list(opp_combo) + list(state.community_cards))

            stronger_hand = StrongestFinalHandFinder.find_stronger_hand(my_final_hand, opp_final_hand)

            if my_final_hand is stronger_hand:
                t_key = 'ahead'
            elif opp_final_hand is stronger_hand:
                t_key = 'behind'
            else:
                t_key = 'tied'

            total_hand_potential[t_key] += 1

            community_combos = self._create_community_combinations(opp_combo, state)

            for comm_combo in community_combos:
                my_end_hand = StrongestFinalHandFinder.find(self.get_hand() + comm_combo)
                opp_end_hand = StrongestFinalHandFinder.find(list(opp_combo) + comm_combo)
                stronger_hand = StrongestFinalHandFinder.find_stronger_hand(my_end_hand, opp_end_hand)

                if my_end_hand is stronger_hand:
                    key = 'ahead'
                elif opp_end_hand is stronger_hand:
                    key = 'behind'
                else:
                    key = 'tied'

                hand_potential[t_key][key] += 1

        ppot = (
                       hand_potential['behind']['ahead'] +
                       (hand_potential['behind']['tied'] / 2) +
                       (hand_potential['tied']['ahead'] / 2)
               ) / (
                       total_hand_potential['behind'] + total_hand_potential['tied']
               )

        npot = (
                       hand_potential['ahead']['behind'] +
                       (hand_potential['tied']['behind'] / 2) +
                       (hand_potential['ahead']['tied'] / 2)
               ) / (
                       total_hand_potential['ahead'] + total_hand_potential['tied']
               )

        hs = (
                     total_hand_potential['ahead'] + (total_hand_potential['tied'] / 2)
             ) / (
                     total_hand_potential['ahead'] + total_hand_potential['tied'] + total_hand_potential['behind']
             )

        hs **= (state.total_players - 1)

        return hs, npot / 1000, ppot / 1000

    def _create_opponent_hand_combinations(self, state: State) -> List[Tuple[Card, Card]]:
        deck = Deck().get_cards()
        indexes = []
        popped_cards = 0
        opponent_hand_combinations = []

        for i, c in enumerate(deck):
            if c in self.get_hand() or c in state.community_cards:
                indexes.append(i)

        for i in indexes:
            deck.pop(i - popped_cards)
            popped_cards += 1

        for i, c1 in enumerate(deck):
            for c2 in deck[i + 1:]:
                opponent_hand_combinations.append((c1, c2))

        return opponent_hand_combinations

    def _create_community_combinations(self, opp_hand: Tuple[Card, Card], state: State) -> List[List[Card]]:
        deck = Deck().get_cards()
        indexes = []
        popped_cards = 0
        community_combos = []
        nbr_of_comm_cards = len(state.community_cards)

        if nbr_of_comm_cards >= 5:
            community_combos.append(state.community_cards)

        else:

            for i, c in enumerate(deck):
                if c in self.get_hand() or c in state.community_cards or c in opp_hand:
                    indexes.append(i)

            for i in indexes:
                deck.pop(i - popped_cards)
                popped_cards += 1

            if nbr_of_comm_cards < 3:
                for i1, c1 in enumerate(deck):
                    for i2, c2 in enumerate(deck[i1 + 1:]):
                        for i3, c3 in enumerate(deck[i2 + 1:]):
                            for i4, c4 in enumerate(deck[i3 + 1:]):
                                for c5 in deck[i4 + 1:]:
                                    community_combos.append([c1, c2, c3, c4, c5])

            elif nbr_of_comm_cards < 4:
                for i, c1 in enumerate(deck):
                    for c2 in deck[i + 1:]:
                        community_combos.append(list(state.community_cards) + [c1, c2])

            elif nbr_of_comm_cards < 5:
                for c in deck:
                    community_combos.append(list(state.community_cards) + [c])

        return community_combos

from enum import Enum


class FinalHandType(Enum):
    HIGH_CARD = 1
    PAIR = 20
    TWO_PAIRS = 300
    TRIS = 4000
    STRAIGHT = 15000
    FLUSH = 33000
    FULL_HOUSE = 500000
    POKER = 6600000
    STRAIGHT_FLUSH = 21500000
    ROYAL_FLUSH = 22000000

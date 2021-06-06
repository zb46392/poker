from . import OpponentBot
from typing import Optional


class OpponentBotSilver(OpponentBot):
    def __init__(self, chips: int, name: Optional[str]):
        fold_thresh = 50
        raise_thresh = 50
        bluff_thresh = 70
        super().__init__(chips, name, fold_thresh, raise_thresh, bluff_thresh)

from . import OpponentBot
from typing import Optional


class OpponentBotSilver(OpponentBot):
    def __init__(self, chips: int, name: Optional[str]):
        fold_thresh = 60
        raise_thresh = 40
        bluff_thresh = 60
        super().__init__(chips, name, fold_thresh, raise_thresh, bluff_thresh)

from . import OpponentBot
from typing import Optional


class OpponentBotGold(OpponentBot):
    def __init__(self, chips: int, name: Optional[str] = None):
        fold_thresh = 40
        raise_thresh = 40
        bluff_thresh = 50
        super().__init__(chips, name, fold_thresh, raise_thresh, bluff_thresh)

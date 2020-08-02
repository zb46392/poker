from . import OpponentBot


class OpponentBotGold(OpponentBot):
    def __init__(self, chips: int):
        fold_thresh = 40
        raise_thresh = 40
        bluff_thresh = 50
        super().__init__(chips, fold_thresh, raise_thresh, bluff_thresh)

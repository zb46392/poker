from . import OpponentBot


class OpponentBotSilver(OpponentBot):
    def __init__(self, chips: int):
        fold_thresh = 60
        raise_thresh = 40
        bluff_thresh = 60
        super().__init__(chips, fold_thresh, raise_thresh, bluff_thresh)

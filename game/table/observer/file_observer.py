from . import TextualObserver
from game import Logger
from typing import Optional


class FileObserver(TextualObserver):
    def __init__(self, log_file_path: Optional[str] = None) -> None:
        super().__init__()
        self._logger = Logger(log_file_path)

    def _apply_new_msg(self, msg: str) -> None:
        self._logger.log(msg)

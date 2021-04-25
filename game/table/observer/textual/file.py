from .base import Base
from game import Logger
from typing import Optional


class File(Base):
    def __init__(self, log_file_path: Optional[str] = None) -> None:
        super().__init__()
        self._logger = Logger(log_file_path)

    def _apply_new_info(self) -> None:
        self._logger.log(self._info)

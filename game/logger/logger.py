from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    def __init__(self, log_file_path: Optional[str] = None) -> None:
        self._log_path: Path
        self._define_log(log_file_path)

    def _define_log(self, log_file_path: Optional[str]) -> None:
        if log_file_path is None:
            self._create_default_log()
        else:
            self._log_path = Path(log_file_path)
            self._ensure_log_directory_existence()

    def _create_default_log(self) -> None:
        log_dir_name = 'log'
        project_path = self._find_project_path()
        log_dir_path = project_path.joinpath(log_dir_name)
        log_dir_path.mkdir(parents=True, exist_ok=True)
        self._create_unique_log_file(log_dir_path)

    def _ensure_log_directory_existence(self) -> None:
        Path(self._log_path.parent).mkdir(parents=True, exist_ok=True)

    def _create_unique_log_file(self, log_dir_path: Path) -> None:
        extension = 'txt'
        log_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_path = log_dir_path.joinpath('.'.join([log_name, extension]))
        cnt = 0

        while log_path.exists():
            log_path = log_dir_path.joinpath('.'.join([log_name, '_', str(cnt), extension]))
            cnt += 1

        with open(str(log_path), 'w') as file:
            file.write('')

        self._log_path = log_path

    @staticmethod
    def _find_project_path() -> Path:
        this_path = Path(__file__)
        return Path(this_path.parent.parent.parent)

    def log(self, text: str) -> None:
        with open(str(self._log_path), 'a') as file:
            file.write(text + '\n')

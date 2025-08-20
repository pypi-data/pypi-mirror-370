from pathlib import Path
from typing import Callable, Dict, List


class FS:
    """Handles filesystem operations"""

    def __init__(self, files: List[Path], file_match: Callable[[Path], bool] | None = None):
        self.files = files
        self.file_match = file_match or (lambda p: p.is_file())

    def all_files_modifications(self) -> Dict[Path, float]:
        """Returns a dict of Path -> modification time"""
        return {
            p: self.file_timestamp(p)
            for p in sum(map(self.all_files_recur, self.files), [])
        }

    def all_files_recur(self, path: Path) -> List[Path]:
        """Returns all files in `path`"""
        if path.is_file():
            return [path] if self.file_match(path) else []
        elif path.is_dir():
            return sum(map(self.all_files_recur, path.iterdir()), [])
        else:
            return []

    @staticmethod
    def file_timestamp(path: Path) -> float:
        return path.stat().st_mtime

    @staticmethod
    def to_path(filepath: str) -> Path:
        return Path(filepath)


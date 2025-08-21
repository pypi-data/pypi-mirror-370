from pathlib import Path
from typing import Optional


class CrossPlatformUtils:
    @staticmethod
    def get_user_documents_directory() -> Path:
        try:
            home = Path.home()
            documents = home / "Documents"
            if documents.exists():
                return documents
            return home
        except Exception:
            return Path.cwd()

    @staticmethod
    def normalize_path(path_str: str) -> Path:
        return Path(path_str).resolve()

    @staticmethod
    def ensure_directory_exists(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def is_hidden_file(path: Path) -> bool:
        return path.name.startswith(".") and path.name not in [".gitignore", ".gitkeep"]

    @staticmethod
    def get_relative_path(file_path: Path, base_path: Path) -> Path:
        try:
            return file_path.relative_to(base_path)
        except ValueError:
            return file_path


def get_user_home_directory() -> str:
    return str(CrossPlatformUtils.get_user_documents_directory())

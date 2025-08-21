from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class FileInfo:
    path: Path
    size_bytes: int
    content: Optional[str] = None
    error: Optional[str] = None
    is_binary: bool = False


@dataclass
class DirectoryMetadata:
    total_files: int
    total_size_bytes: int
    languages_detected: List[str]
    file_types: Dict[str, int]


@dataclass
class ProjectSummary:
    name: str
    root_path: Path
    metadata: DirectoryMetadata
    directory_structure: Dict[str, Any]
    file_contents: Dict[str, FileInfo]


class IFileReader(ABC):
    @abstractmethod
    async def read_file(self, file_path: Path, max_size_kb: int) -> FileInfo:
        pass

    @abstractmethod
    async def read_files_batch(self, file_paths: List[Path], max_size_kb: int) -> List[FileInfo]:
        pass


class IDirectoryAnalyzer(ABC):
    @abstractmethod
    async def analyze_directory(self, root_path: Path) -> DirectoryMetadata:
        pass

    @abstractmethod
    async def get_directory_structure(self, root_path: Path) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_filtered_files(
        self, root_path: Path, include_patterns: List[str], exclude_patterns: List[str]
    ) -> List[Path]:
        pass


class IOutputFormatter(ABC):
    @abstractmethod
    def format_output(self, summary: ProjectSummary) -> str:
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        pass


class IConfigurationProvider(ABC):
    @abstractmethod
    def get_include_patterns(self) -> List[str]:
        pass

    @abstractmethod
    def get_exclude_patterns(self) -> List[str]:
        pass

    @abstractmethod
    def get_max_file_size_kb(self) -> int:
        pass

    @abstractmethod
    def get_output_formats(self) -> List[str]:
        pass

    @abstractmethod
    def get_output_directory(self) -> Path:
        pass

    @abstractmethod
    def set_exclude_patterns(self, patterns: List[str]) -> None:
        pass


class IProgressReporter(ABC):
    @abstractmethod
    def start_progress(self, total_items: int, description: str) -> None:
        pass

    @abstractmethod
    def update_progress(self, increment: int = 1) -> None:
        pass

    @abstractmethod
    def finish_progress(self) -> None:
        pass


class IProjectAnalyzer(ABC):
    @abstractmethod
    async def analyze_project(
        self, root_path: Path, config: IConfigurationProvider
    ) -> ProjectSummary:
        pass


class IOutputWriter(ABC):
    @abstractmethod
    async def write_output(
        self, summary: ProjectSummary, output_dir: Path, formatters: List[IOutputFormatter]
    ) -> List[Path]:
        pass

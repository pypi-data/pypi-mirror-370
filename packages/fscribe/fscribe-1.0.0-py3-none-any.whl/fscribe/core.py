import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from .analyzer import FileSystemAnalyzer
from .exceptions import FscribeException
from .file_reader import AsyncFileReader
from .formatters import JsonFormatter, MarkdownFormatter, TextFormatter
from .interfaces import (
    FileInfo,
    IConfigurationProvider,
    IOutputWriter,
    IProgressReporter,
    IProjectAnalyzer,
    ProjectSummary,
)
from .progress import ConsoleProgressReporter
from .writer import FileOutputWriter


class ProjectAnalysisService(IProjectAnalyzer):
    def __init__(
        self,
        directory_analyzer: Optional[FileSystemAnalyzer] = None,
        file_reader: Optional[AsyncFileReader] = None,
        progress_reporter: Optional[IProgressReporter] = None,
        output_writer: Optional[IOutputWriter] = None,
    ):
        self._directory_analyzer = directory_analyzer or FileSystemAnalyzer()
        self._file_reader = file_reader or AsyncFileReader()
        self._progress_reporter = progress_reporter or ConsoleProgressReporter()
        self._output_writer = output_writer or FileOutputWriter()

    async def analyze_project(
        self, root_path: Path, config: IConfigurationProvider
    ) -> ProjectSummary:
        if not root_path.exists():
            raise FscribeException(f"Directory does not exist: {root_path}")

        if not root_path.is_dir():
            raise FscribeException(f"Path is not a directory: {root_path}")

        metadata = await self._directory_analyzer.analyze_directory(root_path)
        directory_structure = await self._directory_analyzer.get_directory_structure(root_path)

        filtered_files = self._directory_analyzer.get_filtered_files(
            root_path, config.get_include_patterns(), config.get_exclude_patterns()
        )

        self._progress_reporter.start_progress(len(filtered_files), "Reading files")

        file_results = await self._file_reader.read_files_batch(
            filtered_files, config.get_max_file_size_kb()
        )

        file_contents = {}
        for file_info in file_results:
            relative_path = str(file_info.path.relative_to(root_path))
            file_contents[relative_path] = file_info
            self._progress_reporter.update_progress()

        self._progress_reporter.finish_progress()

        return ProjectSummary(
            name=root_path.name,
            root_path=root_path,
            metadata=metadata,
            directory_structure=directory_structure,
            file_contents=file_contents,
        )

    async def analyze_and_save(self, root_path: Path, config: IConfigurationProvider) -> List[Path]:
        summary = await self.analyze_project(root_path, config)

        formatters = self._get_formatters(config.get_output_formats())
        output_files = await self._output_writer.write_output(
            summary, config.get_output_directory(), formatters
        )

        print(f"Project summary saved to {config.get_output_directory()}")
        return output_files

    def _get_formatters(self, format_names: List[str]) -> List[Any]:
        formatter_map = {
            "text": TextFormatter(),
            "json": JsonFormatter(),
            "md": MarkdownFormatter(),
        }

        return [formatter_map[name] for name in format_names if name in formatter_map]

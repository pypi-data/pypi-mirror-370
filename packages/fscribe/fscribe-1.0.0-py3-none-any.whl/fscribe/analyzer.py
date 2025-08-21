import asyncio
import fnmatch
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

from .exceptions import DirectoryAnalysisError
from .interfaces import DirectoryMetadata, IDirectoryAnalyzer


class FileSystemAnalyzer(IDirectoryAnalyzer):
    def __init__(self) -> None:
        self._language_extensions = {
            "Python": [".py", ".pyw"],
            "JavaScript": [".js", ".jsx", ".mjs"],
            "TypeScript": [".ts", ".tsx"],
            "HTML": [".html", ".htm"],
            "CSS": [".css", ".scss", ".sass", ".less"],
            "Markdown": [".md", ".mdx"],
            "C#": [".cs", ".csproj", ".sln"],
            "C++": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
            "C": [".c", ".h"],
            "Java": [".java"],
            "Go": [".go"],
            "Rust": [".rs"],
            "PHP": [".php"],
            "Ruby": [".rb"],
            "Shell": [".sh", ".bash", ".zsh"],
            "JSON": [".json"],
            "YAML": [".yml", ".yaml"],
            "XML": [".xml"],
            "SQL": [".sql"],
            "Docker": ["Dockerfile", ".dockerignore"],
            "Config": [".toml", ".ini", ".cfg", ".conf"],
        }

    async def analyze_directory(self, root_path: Path) -> DirectoryMetadata:
        try:
            total_files: int = 0
            total_size: int = 0
            language_counts: Dict[str, int] = defaultdict(int)
            file_type_counts: Dict[str, int] = defaultdict(int)

            for file_path in root_path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_stats = file_path.stat()
                        total_files += 1
                        total_size += file_stats.st_size

                        file_ext = file_path.suffix.lower()
                        file_type_counts[file_ext] += 1

                        for language, extensions in self._language_extensions.items():
                            if file_ext in extensions or file_path.name in extensions:
                                language_counts[language] += 1
                                break
                    except (OSError, PermissionError):
                        continue

            languages_detected = [lang for lang, count in language_counts.items() if count > 0]

            return DirectoryMetadata(
                total_files=total_files,
                total_size_bytes=total_size,
                languages_detected=languages_detected,
                file_types=dict(file_type_counts),
            )
        except Exception as e:
            raise DirectoryAnalysisError(str(root_path), e)

    async def get_directory_structure(self, root_path: Path) -> Dict[str, Any]:
        try:
            structure: Dict[str, Any] = {}

            for item in root_path.rglob("*"):
                relative_path = item.relative_to(root_path)
                parts = relative_path.parts

                current_level = structure
                for part in parts[:-1]:
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]

                if parts:
                    final_part = parts[-1]
                    if item.is_file():
                        current_level[final_part] = "file"
                    elif item.is_dir():
                        if final_part not in current_level:
                            current_level[final_part] = {}

            return structure
        except Exception as e:
            raise DirectoryAnalysisError(str(root_path), e)

    def get_filtered_files(
        self, root_path: Path, include_patterns: List[str], exclude_patterns: List[str]
    ) -> List[Path]:
        try:
            all_files = []

            for file_path in root_path.rglob("*"):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(root_path))

                    included = False
                    if include_patterns:
                        for pattern in include_patterns:
                            if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(
                                file_path.name, pattern
                            ):
                                included = True
                                break
                    else:
                        included = True

                    excluded = False
                    for pattern in exclude_patterns:
                        if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(
                            file_path.name, pattern
                        ):
                            excluded = True
                            break

                    if included and not excluded:
                        all_files.append(file_path)

            return all_files
        except Exception as e:
            raise DirectoryAnalysisError(str(root_path), e)

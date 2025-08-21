import json
from pathlib import Path
from typing import Any, Dict

from .interfaces import IOutputFormatter, ProjectSummary


class TextFormatter(IOutputFormatter):
    def format_output(self, summary: ProjectSummary) -> str:
        lines = [
            f"PROJECT SUMMARY: {summary.name}",
            "",
            "DIRECTORY STRUCTURE:",
            self._format_directory_tree(summary.directory_structure),
            "",
            "FILE CONTENTS:",
        ]

        for file_path, file_info in summary.file_contents.items():
            if file_info.content:
                lines.extend([f"--- {file_path} ---", file_info.content, ""])

        lines.extend(
            [
                "",
                "SUMMARY:",
                f"- Total Files: {summary.metadata.total_files}",
                f"- Total Size: {summary.metadata.total_size_bytes // 1024} KB",
                f"- Languages Used: {', '.join(summary.metadata.languages_detected)}",
            ]
        )

        return "\n".join(lines)

    def get_file_extension(self) -> str:
        return ".txt"

    def _format_directory_tree(
        self, structure: Dict[str, Any], prefix: str = "", is_root: bool = True
    ) -> str:
        lines = []
        items = list(structure.items())

        for i, (name, content) in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "|-- " if not is_root else ""

            if content == "file":
                lines.append(f"{prefix}{current_prefix}{name}")
            else:
                lines.append(f"{prefix}{current_prefix}{name}/")
                if isinstance(content, dict):
                    next_prefix = prefix + ("    " if is_last else "|   ")
                    lines.append(self._format_directory_tree(content, next_prefix, False))

        return "\n".join(filter(None, lines))


class JsonFormatter(IOutputFormatter):
    def format_output(self, summary: ProjectSummary) -> str:
        file_contents = {}
        for file_path, file_info in summary.file_contents.items():
            if file_info.content:
                file_contents[file_path] = file_info.content

        output_data = {
            "project_name": summary.name,
            "root_path": str(summary.root_path),
            "directory_structure": summary.directory_structure,
            "file_contents": file_contents,
            "summary": {
                "total_files": summary.metadata.total_files,
                "total_size_bytes": summary.metadata.total_size_bytes,
                "total_size_kb": summary.metadata.total_size_bytes // 1024,
                "languages_detected": summary.metadata.languages_detected,
                "file_types": summary.metadata.file_types,
            },
        }

        return json.dumps(output_data, indent=4, ensure_ascii=False)

    def get_file_extension(self) -> str:
        return ".json"


class MarkdownFormatter(IOutputFormatter):
    def format_output(self, summary: ProjectSummary) -> str:
        lines = [
            f"# {summary.name} Project Summary",
            "",
            "## Directory Structure",
            "```",
            self._format_directory_tree(summary.directory_structure),
            "```",
            "",
            "## File Contents",
        ]

        for file_path, file_info in summary.file_contents.items():
            if file_info.content:
                file_extension = Path(file_path).suffix.lstrip(".")
                language = self._get_language_for_extension(file_extension)

                lines.extend([f"### {file_path}", f"```{language}", file_info.content, "```", ""])

        lines.extend(
            [
                "## Summary",
                f"- **Total Files:** {summary.metadata.total_files}",
                f"- **Total Size:** {summary.metadata.total_size_bytes // 1024} KB",
                f"- **Languages Used:** {', '.join(summary.metadata.languages_detected)}",
            ]
        )

        return "\n".join(lines)

    def get_file_extension(self) -> str:
        return ".md"

    def _format_directory_tree(self, structure: Dict[str, Any], prefix: str = "") -> str:
        lines = []
        items = list(structure.items())

        for i, (name, content) in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "|-- "

            if content == "file":
                lines.append(f"{prefix}{current_prefix}{name}")
            else:
                lines.append(f"{prefix}{current_prefix}{name}/")
                if isinstance(content, dict):
                    next_prefix = prefix + ("    " if is_last else "|   ")
                    lines.append(self._format_directory_tree(content, next_prefix))

        return "\n".join(filter(None, lines))

    def _get_language_for_extension(self, extension: str) -> str:
        language_map = {
            "py": "python",
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "html": "html",
            "css": "css",
            "md": "markdown",
            "cs": "csharp",
            "cpp": "cpp",
            "c": "c",
            "java": "java",
            "go": "go",
            "rs": "rust",
            "php": "php",
            "rb": "ruby",
            "sh": "bash",
            "json": "json",
            "yml": "yaml",
            "yaml": "yaml",
            "xml": "xml",
            "sql": "sql",
        }
        return language_map.get(extension.lower(), "plaintext")

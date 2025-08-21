import asyncio
from pathlib import Path
from typing import List

import aiofiles

from .exceptions import OutputWriteError
from .interfaces import IOutputFormatter, IOutputWriter, ProjectSummary


class FileOutputWriter(IOutputWriter):
    async def write_output(
        self, summary: ProjectSummary, output_dir: Path, formatters: List[IOutputFormatter]
    ) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        def sanitize_filename(name: str) -> str:
            import re

            name = re.sub(r"[^\w\-. ]", "_", name)
            name = re.sub(r"\s+", "_", name)
            return name

        output_files = []
        write_tasks = []

        for formatter in formatters:
            safe_name = sanitize_filename(summary.name)
            output_file = output_dir / f"{safe_name}{formatter.get_file_extension()}"
            try:
                output_file.relative_to(output_dir)
            except ValueError as e:
                raise OutputWriteError(str(output_file), e)

            if output_file.exists():
                raise OutputWriteError(
                    str(output_file), Exception("Refusing to overwrite existing file.")
                )

            content = formatter.format_output(summary)
            write_tasks.append(self._write_file(output_file, content))
            output_files.append(output_file)

        await asyncio.gather(*write_tasks)
        return output_files

    async def _write_file(self, file_path: Path, content: str) -> None:
        try:
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(content)
        except Exception as e:
            raise OutputWriteError(str(file_path), e)

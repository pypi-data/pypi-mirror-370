import asyncio
from pathlib import Path
from typing import List, Optional

import aiofiles

from .exceptions import FileReadError
from .interfaces import FileInfo, IFileReader


class AsyncFileReader(IFileReader):
    def __init__(self, max_concurrent_reads: int = 10):
        self._semaphore = asyncio.Semaphore(max_concurrent_reads)

    async def read_file(self, file_path: Path, max_size_kb: int) -> FileInfo:
        async with self._semaphore:
            return await self._read_single_file(file_path, max_size_kb)

    async def read_files_batch(self, file_paths: List[Path], max_size_kb: int) -> List[FileInfo]:
        tasks = [self.read_file(file_path, max_size_kb) for file_path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def _read_single_file(self, file_path: Path, max_size_kb: int) -> FileInfo:
        try:
            file_stats = file_path.stat()
            size_bytes = file_stats.st_size

            if size_bytes > max_size_kb * 1024:
                return FileInfo(
                    path=file_path,
                    size_bytes=size_bytes,
                    error=f"File too large ({size_bytes // 1024} KB > {max_size_kb} KB)",
                )

            if self._is_binary_file(file_path):
                return FileInfo(
                    path=file_path, size_bytes=size_bytes, is_binary=True, error="Binary file"
                )

            content = await self._read_text_content(file_path)

            return FileInfo(path=file_path, size_bytes=size_bytes, content=content)

        except PermissionError:
            return FileInfo(path=file_path, size_bytes=0, error="Permission denied")
        except Exception as e:
            return FileInfo(path=file_path, size_bytes=0, error=str(e))

    async def _read_text_content(self, file_path: Path) -> str:
        encodings = ["utf-8", "utf-16", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                async with aiofiles.open(file_path, "r", encoding=encoding, errors="ignore") as f:
                    content = await f.read()
                    return content.strip()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise FileReadError(str(file_path), e)

        raise FileReadError(
            str(file_path), Exception("Could not decode file with any supported encoding")
        )

    def _is_binary_file(self, file_path: Path) -> bool:
        binary_extensions = {
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".bin",
            ".obj",
            ".class",
            ".jar",
            ".war",
            ".ear",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
            ".7z",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".ico",
            ".svg",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".wav",
            ".flac",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
        }

        return file_path.suffix.lower() in binary_extensions or self._contains_null_bytes(file_path)

    def _contains_null_bytes(self, file_path: Path) -> bool:
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                return b"\x00" in chunk
        except Exception:
            return True

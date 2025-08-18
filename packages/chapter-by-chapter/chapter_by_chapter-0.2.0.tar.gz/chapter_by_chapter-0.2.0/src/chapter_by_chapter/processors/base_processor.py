# Chapter by Chapter - A Mastodon bot for serializing classic literature
# Copyright (C) 2025 Bryan L. Fordham
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from abc import ABC, abstractmethod
from pathlib import Path

from robotooter.filters.base_filter import BaseFilter


class BaseProcessor(ABC):
    def __init__(self, book_key: str, output_dir: Path, file_path: Path, max_chunk_size: int) -> None:
        self.book_key = book_key
        self.output_dir = output_dir
        self.file_path = file_path
        self.max_chunk_size = max_chunk_size

        self.filters: list[BaseFilter] = []

    @abstractmethod
    def process_file(self) -> None:
        pass

    def chunk_chapter(self, book_key: str, chapter: int, text: list[str]) -> None:
        chunk = ''
        part = 1
        for line in text:
            if len(chunk) + len(line) >= self.max_chunk_size:
                self._write_chunk(book_key, chapter, part, chunk)
                part += 1
                chunk = ''
            chunk += line
        if chunk:
            self._write_chunk(book_key, chapter, part, chunk)

    def _write_chunk(self, book_key: str, chapter: int, part: int, chunk: str) -> None:
        c = str(chapter).zfill(4)
        p = str(part).zfill(4)
        chunk_path = self.output_dir / book_key / f"{c}_{p}.txt"
        with open(chunk_path, "w") as chunk_file:
            chunk_file.write(chunk)

    def _chapter_metadata_path(self, book_key: str, chapter: int) -> Path:
        base = f"{str(chapter).zfill(4)}"
        return self.output_dir / book_key / f"{base}_metadata.json"


    def _make_destination_dir(self, book_key: str) -> Path:
        destination_dir = self.output_dir / book_key
        destination_dir.mkdir(parents=True, exist_ok=True)
        return destination_dir

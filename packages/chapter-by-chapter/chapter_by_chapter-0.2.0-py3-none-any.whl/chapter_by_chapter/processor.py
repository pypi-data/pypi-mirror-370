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

import re
import tempfile
from pathlib import Path
from typing import Type

import requests

from chapter_by_chapter.processors.base_processor import BaseProcessor
from chapter_by_chapter.processors.gutenberg import GutenbergTextProcessor
from chapter_by_chapter.processors.gutenberg.gutenberg_html import GutenbergHtmlProcessor

RE_PART = re.compile(r"^PART (.+?)\.$")
RE_CHAPTER = re.compile(r"^CHAPTER (.+?)\.$")

MAX_CHUNK_SIZE = 2000


class Processor:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def process_url(self, book_key:str, url:str) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            destination_dir = Path(tmp_dir)
            ext = Path(url).suffix
            downloaded = destination_dir / f"_downloaded{ext}"
            req = requests.get(url)
            with downloaded.open("w") as f:
                f.write(req.text)
            self.process_file(book_key, downloaded)

    def process_file(self, book_key: str, file_path: Path) -> None:
        file_extension = file_path.suffix
        processor_class: Type[BaseProcessor]
        if file_extension == ".html":
            processor_class = GutenbergHtmlProcessor
        elif file_extension == ".txt":
            processor_class = GutenbergTextProcessor
        else:
            raise RuntimeError(f"Unsupported file extension: {file_extension}")
        processor = processor_class(
            book_key, output_dir=self.output_dir, file_path=file_path, max_chunk_size=MAX_CHUNK_SIZE
        )
        processor.process_file()


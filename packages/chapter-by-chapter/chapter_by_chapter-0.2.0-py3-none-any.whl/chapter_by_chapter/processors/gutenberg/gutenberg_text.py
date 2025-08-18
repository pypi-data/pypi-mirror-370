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
from pathlib import Path

from robotooter.file_filter import FileFilter
from robotooter.filters.gutenberg import GutenbergFilter
from robotooter.filters.paragraph_combining import ParagraphCombiningFilter

from chapter_by_chapter.models import BookMetadata, ChapterMetadata
from chapter_by_chapter.processors.base_processor import BaseProcessor

RE_PART = re.compile(r"^PART (.+?)\.$")
RE_CHAPTER = re.compile(r"^CHAPTER (.+?)\.$")


class GutenbergTextProcessor(BaseProcessor):
    def __init__(self, book_key: str, output_dir: Path, file_path: Path, max_chunk_size: int) -> None:
        super().__init__(book_key=book_key, output_dir=output_dir, file_path=file_path, max_chunk_size=max_chunk_size)
        self.filters = [GutenbergFilter(), ParagraphCombiningFilter()]

    def process_file(self) -> None:
        destination_dir = self._make_destination_dir(self.book_key)

        file_filter = FileFilter(self.filters)
        pre_process_path = destination_dir / "pre_processed.txt"
        file_filter.process_file(self.file_path, pre_process_path)

        with open(pre_process_path, "r") as file:
            title = file.readline().strip()
            file.readline()
            author = file.readline().strip()

            # skip next few lines
            for _ in range(5):
                file.readline()

            # skip through contents
            line = ''
            while line.strip() != f"{title}.":
                line = file.readline()

            # We're now down with the front matter
            counter = 0
            section_counter = 0
            section = ''
            section_title = ''
            section_start = False
            chapter = ''
            chapter_title = ''
            chapter_lines: list[str] = []
            for raw_line in file:
                line = raw_line.strip()

                if RE_PART.match(line):
                    section_counter += 1
                    section = line
                    section_title = ''
                    continue

                if RE_CHAPTER.match(line):
                    chapter = line
                    chapter_title = ''
                    continue

                if section and not section_title:
                    section_title = line
                    section_start = True
                    continue

                if chapter and not chapter_title:
                    chapter_title = line

                    if chapter_lines:
                        self.chunk_chapter(self.book_key, counter, chapter_lines)
                        chapter_lines = []
                    counter += 1

                    chapter_metadata = ChapterMetadata(
                        section=section,
                        section_title=section_title,
                        section_start=section_start,
                        chapter_title=chapter_title,
                        chapter_label=chapter,
                        chapter_number=counter,
                        chapter_start=True
                    )
                    with open(self._chapter_metadata_path(self.book_key, counter), "w") as md_file:
                        md_file.write(chapter_metadata.model_dump_json(indent=2))
                    section_start = False

                    chapter_lines.append(f"{chapter}\n{chapter_title}\n")
                    continue

                if chapter_title:
                    chapter_lines.append(raw_line)
            if chapter_lines:
                self.chunk_chapter(self.book_key, counter, chapter_lines)

            book_metadata = BookMetadata(
                title=title,
                author=author,
                total_chapters=counter,
                total_sections=section_counter,
            )
            with open(self.output_dir / self.book_key / "book_metadata.json", "w") as md_file:
                md_file.write(book_metadata.model_dump_json(indent=2))

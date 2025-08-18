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

from bs4 import BeautifulSoup
from robotooter.file_filter import FileFilter
from robotooter.filters.paragraph_combining import ParagraphCombiningFilter

from chapter_by_chapter.models import BookMetadata, ChapterMetadata
from chapter_by_chapter.processors.base_processor import BaseProcessor

RE_PART = re.compile(r"^PART (.+?)\.\n")


class GutenbergHtmlProcessor(BaseProcessor):
    def __init__(self, book_key: str, output_dir: Path, file_path: Path, max_chunk_size: int) -> None:
        super().__init__(book_key=book_key, output_dir=output_dir, file_path=file_path, max_chunk_size=max_chunk_size)

    def process_file(self) -> None:
        destination_dir = self._make_destination_dir(self.book_key)

        file_filter = FileFilter(self.filters)
        pre_process_path = destination_dir / "pre_processed.txt"
        file_filter.process_file(self.file_path, pre_process_path)

        soup = BeautifulSoup(self.file_path.read_text(), 'html.parser')

        title_tag = soup.find('meta', attrs={'name':'dc.title'})
        if not title_tag:
            raise RuntimeError(f"No title tag found in {self.file_path}")
        title = title_tag.get('content') # type: ignore
        author_tag = soup.find('meta', attrs={'name':'dc.creator'})
        if not author_tag:
            raise RuntimeError(f"No author tag found for {self.book_key}")
        author_info = author_tag.get('content') # type: ignore
        # We're now down with the front matter
        counter = 0
        section_counter = 0
        section = ''
        section_title = ''
        section_start = False

        html_chapters = soup.find_all('div', attrs={'class':'chapter'})
        # We want the ones that start after the table of contents
        html_chapters = html_chapters[1:] # type: ignore
        while html_chapters:
            possible= html_chapters[0]
            html_chapters = html_chapters[1:] # type: ignore
            if RE_PART.match(possible.text):
                break
            try:
                chapter, _, _ = possible.text.strip().split('\n', 2)
                if chapter:
                    break
            except Exception:
                pass

        if not html_chapters:
            raise RuntimeError(f"No chapters found in {self.file_path}")

        for chap in html_chapters:
            text = chap.text.strip()

            if RE_PART.match(text):
                section_counter += 1
                section, section_title = text.split('\n', 1)
                section_start = True
                section = section.strip()
                section_title = section_title.strip()
                continue

            chapter, chapter_title, chapter_text = text.split('\n', 2)
            counter += 1
            chapter_lines =  [f"{chapter}\n{chapter_title}\n\n"]
            # Now we need to combine things into paragraphs
            pcf = ParagraphCombiningFilter()

            for line in chapter_text.splitlines():
                result = pcf.process(line)
                if result is not None:
                    chapter_lines.append(result)
            last_part = pcf.finalize()
            if last_part:
                chapter_lines.append(last_part)

            self.chunk_chapter(self.book_key, counter, chapter_lines)

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

        last_name, first_name, years = author_info.split(', ')

        book_metadata = BookMetadata(
            title=title,
            author=f"{first_name} {last_name}",
            author_years=years,
            total_chapters=counter,
            total_sections=section_counter,
        )
        with open(self.output_dir / self.book_key / "book_metadata.json", "w") as md_file:
            md_file.write(book_metadata.model_dump_json(indent=2))

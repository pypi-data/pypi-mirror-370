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
from enum import StrEnum
from typing import Union

from robotooter.models.configs import BotConfig
from robotooter.models.saveable_model import SaveableModel
from robotooter.models.statuses import RtStatus


class BookMetadata(SaveableModel):
    title: str
    author: str
    author_years: str = ''
    about_author: str = ''
    about_book: str = ''
    about_author_link: str = ''
    about_book_link: str = ''
    first_link: str = ''
    total_chapters: int = 0
    total_sections: int = 0
    current_day: int = 1
    schedule: str = ''
    tags: list[str] = []
    emoji: str = ''

    @property
    def book_key(self) -> str | None:
        if not self.filename:
            return None
        import os
        return os.path.basename(self.filename.parent)

    @property
    def days_remaining(self) -> int:
        return self.total_chapters - self.current_day


class ChapterMetadata(SaveableModel):
    section: str
    section_title: str = ''
    section_start: bool
    chapter_number: int = 0
    chapter_label: str = ''
    chapter_title: str = ''
    chapter_start: bool = False
    previous_link: str = ''


class ChapterStatus(RtStatus):
    template: str | None = None


class PeriodicMessages(StrEnum):
    MaintainerNextBookReminder = 'maintainer_next_book_reminder'

class ChapterByChapterConfig(BotConfig):
    book_key: str = ''
    chapter: int = 0
    book_queue: list[str] = []
    book_selection_method: str = 'next'
    previous_books: list[str] = []
    periodic_message_settings: dict[str, Union[PeriodicMessages | bool | int]] = {}

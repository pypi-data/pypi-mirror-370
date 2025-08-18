from enum import StrEnum

from robotooter.models.configs import BotConfig
from robotooter.models.saveable_model import SaveableModel
from robotooter.models.statuses import RtStatus

class BookMetadata(SaveableModel):
    title: str
    author: str
    author_years: str
    about_author: str
    about_book: str
    about_author_link: str
    about_book_link: str
    first_link: str
    total_chapters: int
    total_sections: int
    current_day: int
    schedule: str
    tags: list[str]
    emoji: str
    @property
    def book_key(self) -> str | None: ...
    @property
    def days_remaining(self) -> int: ...

class ChapterMetadata(SaveableModel):
    section: str
    section_title: str
    section_start: bool
    chapter_number: int
    chapter_label: str
    chapter_title: str
    chapter_start: bool
    previous_link: str

class ChapterStatus(RtStatus):
    template: str | None

class PeriodicMessages(StrEnum):
    MaintainerNextBookReminder = 'maintainer_next_book_reminder'

class ChapterByChapterConfig(BotConfig):
    book_key: str
    chapter: int
    book_queue: list[str]
    book_selection_method: str
    previous_books: list[str]
    periodic_message_settings: dict[str, PeriodicMessages | bool | int]

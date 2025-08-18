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

from argparse import Namespace
from pathlib import Path
from typing import ClassVar, Type

from robotooter.bots.base_bot import BaseBot, CommandParam, command
from robotooter.filters.base_filter import BaseFilter
from robotooter.mixins.resources import ResourcesMixin
from robotooter.models.configs import BotConfig
from robotooter.models.statuses import RtStatus, StatusVisibility

from chapter_by_chapter.content_creator import ContentCreator
from chapter_by_chapter.greeter import Greeter
from chapter_by_chapter.models import BookMetadata, ChapterByChapterConfig, ChapterMetadata, PeriodicMessages
from chapter_by_chapter.processor import Processor

SET_BOOK_PARAMS: list[CommandParam] = [
    ('-bk', '--book', {'type': str, 'help': 'Book key'}),
    ('-cp', '--chapter', {'type': int, 'help': 'Chapter, defaults to 1', 'default': 1}),
]


ENQUEUE_PARAMS: list[CommandParam] = [
    ('-a', '--add', {'type': str, 'help': 'Book to add'}),
    ('-r', '--remove', {'type': str, 'help': 'Remove to add'}),
]

PERIODIC_PARAMS: list[CommandParam] = [
    ('-e', '--enable', {'action': 'store_true', 'help': 'Message to enable'}),
    ('-d', '--disable', {'action': 'store_true', 'help': 'Message to disable'}),
]


class ChapterByChapterBot(ResourcesMixin, BaseBot[ChapterByChapterConfig]):
    CONFIG_CLASS: ClassVar[Type[ChapterByChapterConfig]] = ChapterByChapterConfig

    @classmethod
    def create_with_config(cls, config_data: BotConfig, filters: list[BaseFilter]) -> 'ChapterByChapterBot':
        """Factory method specific to MastodonBot."""
        config = ChapterByChapterConfig(**config_data.model_dump())
        config.filename = config_data.filename
        return cls(config, filters)

    @staticmethod
    def new_bot_info() -> str | None:
        return (
            "To setup a book, you will need to run:\n\n"
            "robotooter -b <botname> setup BOOK\n\n"
            "Where BOOK is a file or URL to the text file for a book Project Gutenberg."
        )

    def __init__(self, config: ChapterByChapterConfig, filters: list[BaseFilter]) -> None:
        super().__init__(config, filters)

        self.command_overrides['setup'] = [
            ('-f', '--file', {'type': str, 'help': 'File to process', 'default': ''}),
            ('-u', '--url', {'type': str, 'help': 'URL to download and process', 'default': ''}),
            ('-bk', '--book', {'type': str, 'help': 'Key to use for the book', 'default': ''}),
        ]

    @command(name='set-book', help_text='Set the current book', params=SET_BOOK_PARAMS)
    def set_book(self, args: Namespace) -> None:
        assert args.book
        chapter = args.chapter
        if not chapter:
            chapter = 1

        self.config.book_key = args.book
        self.config.chapter = args.chapter
        self.config.save()

    @command(name='show-book', help_text='Show the current book')
    def show_book(self, args: Namespace) -> None:
        if not self.config.book_key:
            print("No book is currently selected.")
            return

        current_book = self.get_book_metadata(self.config.book_key)
        if not current_book:
            print("Could not load book metadata.")
            return

        print(f"   Current book: {self.config.book_key}")
        print(f"          Title: {current_book.title}")
        print(f"         Author: {current_book.author}")
        print(f"Current Chapter: {self.config.chapter}")

    @command(name='list-books', help_text='List all books')
    def list_books(self, args: Namespace) -> None:
        for book in self.get_all_books():
            print(book.title)

    @command(name='queue', help_text='List, add, or remove a book to the book queue', params=ENQUEUE_PARAMS)
    def queue(self, args: Namespace) -> None:
        if hasattr(args, 'add') and args.add is not None:
            book_key = args.add
            self._add_to_queue(book_key)
        elif hasattr(args, 'remove') and args.remove is not None:
            book_key = args.remove
            self._remove_from_queue(book_key)
        else:
            self._list_queue()

    @command(name='periodic', help_text='Send periodic messages, if necessary', params=PERIODIC_PARAMS)
    def periodic_message(self, args: Namespace) -> None:
        if hasattr(args, 'enable') and args.enable:
            self.config.periodic_message_settings = {
                PeriodicMessages.MaintainerNextBookReminder: True
            }
            self.config.save()
        elif hasattr(args, 'disable') and args.disable:
            self.config.periodic_message_settings = {
                PeriodicMessages.MaintainerNextBookReminder: False
            }
            print(self.config.periodic_message_settings)
            print(self.config.filename)
            self.config.save()
        else:
            self._handle_maintainer_reminder()

    def _add_to_queue(self, book_key: str) -> None:
        if not self.config.book_key:
            print("No book is currently selected.")
            return

        if book_key in self.config.previous_books:
            print(f"{book_key} already present in list of previous books.")
            return

        if book_key == self.config.book_key:
            print(f"{book_key} is the current book.")
            return

        if book_key in self.config.book_queue:
            print(f"{book_key} is already in book queue.")
            return

        book_metadata = self.get_book_metadata(book_key)
        if not book_metadata:
            print(f"{book_key} not found.")
            return

        self.config.book_queue.append(book_key)
        self.config.save()
        print(f"Added {book_key} to the book queue.")

    def _remove_from_queue(self, book_key: str) -> None:
        book_metadata = self.get_book_metadata(book_key)
        if not book_metadata:
            print(f"{book_key} not found.")
            return

        if book_key not in self.config.book_queue:
            print(f"{book_key} is not in book queue.")
            return

        self.config.book_queue.remove(book_key)
        self.config.save()
        print(f"Removed {book_key} from the book queue.")

    def _list_queue(self) -> None:
        if not self.config.book_queue:
            print("No books are currently present in the book queue.")
            return

        print(f"{len(self.config.book_queue)} books are currently present in the book queue.")
        for i, book in enumerate(self.config.book_queue):
            md = self.get_book_metadata(book)
            if not md:
                raise RuntimeError(f"Could not load book metadata for {book}")
            print(f"{i+1}. {md.title}")

    def generate_content(self, book_key: str | None, chapter: int | None = None) -> None:
        if not book_key:
            book_key = self.config.book_key
        if not chapter:
            chapter = self.config.chapter

        book_metadata = self.get_book_metadata(book_key)
        if not book_metadata:
            raise RuntimeError(f"Could not load metadata for: {book_key}.")
        chapter_metadata, chapter_paths = self.get_chapter_metadata(book_key, chapter)
        if not chapter_metadata:
            raise RuntimeError(f"No chapter metadata found for book key {book_key} at chapter {chapter}")

        tomorrow = self.get_tomorrows_chapter(book_key, chapter)
        next_book = self.get_next_book()

        content_creator = ContentCreator(
            bot_config=self.config,
            book_metadata=book_metadata,
            chapter_metadata=chapter_metadata,
            working_directory=self.working_directory,
            chapter_paths=chapter_paths,
            tomorrow=tomorrow,
            next_book=next_book,
        )

        book_intro_thread = None
        if chapter == 1:
            book_intro_thread = content_creator.create_book_intro()
            self.mastodon_manager.thread(book_intro_thread)
            # update first link for book
            if len(book_intro_thread) and book_intro_thread[0].url:
                book_metadata.first_link = book_intro_thread[0].url
            self._get_json_path(book_key).write_text(book_metadata.model_dump_json(indent=2))

        chapter_thread = content_creator.create_chapter_thread()
        self.mastodon_manager.thread(chapter_thread)

        # update next day's link
        first_chapter_status = chapter_thread[0]
        if tomorrow and first_chapter_status.url:
            tomorrow.previous_link = first_chapter_status.url
            tomorrow.save()

        # update book thread, if it exists
        if book_intro_thread:
            link = content_creator.create_link_to_chapter_thread(
                first_chapter_status, book_intro_thread[-1], len(book_intro_thread)+1
            )
            self.mastodon_manager.toot(link)

        # Update book queue if we've finished the book
        if not tomorrow and next_book:
            self.config.book_key = next_book.book_key or ''
            self.config.chapter = 1
            self.config.book_queue = self.config.book_queue[1:]
            self.config.previous_books.append(book_key)
            self.config.save()

    def _toot(self, args: Namespace) -> None:
        # toot the next chapter of the book
        self.generate_content(self.config.book_key, self.config.chapter)
        self.config.chapter = self.config.chapter + 1
        self.config.save()

    def _setup_data(self, args: Namespace) -> None:
        processor = Processor(self.book_path())
        file_or_url = None
        book_key = None
        if hasattr(args, 'file') and args.file:
            file_or_url = args.file
        elif hasattr(args, 'url') and args.url:
            file_or_url = args.url

        if not file_or_url:
            print("No file path provided.")
            return

        if hasattr(args, 'book') and args.book:
            book_key = args.book

        if not book_key:
            print("No book key provided.")
            return

        if file_or_url.startswith("https"):
            processor.process_url(book_key, file_or_url)
        else:
            processor.process_file(book_key, Path(file_or_url))

    def get_greeter(self) -> Greeter:
        return Greeter(self.resource_path('word_choices.json'))

    def get_all_books(self) -> list[BookMetadata]:
        all = []
        for path in self.book_path().glob('**/book_metadata.json'):
            all.append(BookMetadata.load(path))
        return all

    def get_book_metadata(self, book_key: str) -> BookMetadata | None:
        md_path = self._get_json_path(book_key)
        if not md_path.exists():
            return None
        return BookMetadata.load(md_path)

    def get_chapter_metadata(self, book_key: str, chapter: int) -> tuple[ChapterMetadata|None, list[Path]]:
        book_dir = self.book_path(book_key)
        chapter_base = str(chapter).zfill(4)
        chapter_metadata_path = self._get_json_path(book_key, chapter)
        if not chapter_metadata_path.exists():
            return None, []

        chapter_metadata = ChapterMetadata.load(chapter_metadata_path)
        files = [f for f in book_dir.glob(f"{chapter_base}_[0-9][0-9][0-9][0-9].txt")]
        files.sort()
        return chapter_metadata, files

    def get_tomorrows_chapter(self, book_key: str, chapter:int) -> ChapterMetadata | None:
        md, _ = self.get_chapter_metadata(book_key, chapter+1)
        return md

    def get_next_book(self) -> BookMetadata | None:
        if not self.config.book_queue:
            return None
        next_book = self.config.book_queue[0]
        return self.get_book_metadata(next_book)


    def book_path(self, book_key:str|None = None) -> Path:
        base_path = self.config.working_directory / 'books'
        if not book_key:
            return base_path
        return base_path / book_key

    def get_days_remaining_in_current_book(self) -> int:
        current_book = self.get_book_metadata(self.config.book_key)
        if not current_book:
            return 0
        return current_book.total_chapters - self.config.chapter

    def _handle_maintainer_reminder(self) -> None:
        setting = self._get_periodic_message_settings(PeriodicMessages.MaintainerNextBookReminder)
        if not setting:
            return

        if setting is True:
            setting = 4

        day_trigger = int(setting)
        if self.get_days_remaining_in_current_book() == day_trigger:
            next_book = self.get_next_book()

            if next_book:
                next_book_message = f"The next book scheduled is {next_book.title}"
            else:
                next_book_message = "There currently is not another book in the queue."

            message = [
                f"{self.config.maintainer} Just a reminder that the current book ends in {day_trigger} days.",
                "",
                next_book_message
            ]
            status = RtStatus(
                text='\n'.join(message),
                visibility=StatusVisibility.Direct,
            )
            self.mastodon_manager.toot(status)


    def _get_periodic_message_settings(self, key: PeriodicMessages) -> int | str | bool | None:
        if not self.config.periodic_message_settings or key not in self.config.periodic_message_settings:
            return None
        return self.config.periodic_message_settings[key]

    def _get_json_path(self, book_key:str, chapter: int = 0) -> Path:
        chapter_str = ''
        if chapter:
            chapter_str = str(chapter).zfill(4)
        path = self.book_path(book_key)
        if chapter:
            filename = f"{chapter_str}_metadata.json"
        else:
            filename = "book_metadata.json"
        return path / filename

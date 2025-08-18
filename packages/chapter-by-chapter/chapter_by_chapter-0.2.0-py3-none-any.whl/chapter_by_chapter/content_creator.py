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
from random import choice
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template
from robotooter.models.configs import BotConfig
from robotooter.models.statuses import RtMedia, RtStatus

from chapter_by_chapter.greeter import Greeter
from chapter_by_chapter.models import BookMetadata, ChapterMetadata


class ContentCreator:
    def __init__(
            self,
            bot_config: BotConfig,
            book_metadata: BookMetadata,
            chapter_metadata: ChapterMetadata,
            chapter_paths: list[Path],
            working_directory: Path,
            tomorrow: ChapterMetadata | None,
            next_book: BookMetadata | None,
    ):
        assert book_metadata.book_key

        self.bot_config = bot_config
        self.book_key = book_metadata.book_key
        self.book_metadata = book_metadata
        self.chapter_metadata = chapter_metadata
        self.chapter_paths = chapter_paths
        self.working_directory = working_directory
        self.tomorrow = tomorrow
        self.next_book = next_book

        self.template_base_dir = self.working_directory / 'resources' / 'templates'
        self.template_env = Environment(loader=FileSystemLoader(self.template_base_dir))

    def create_book_intro(self) -> list[RtStatus]:
        intro_templates = ['book_intro']
        if self.book_metadata.about_book:
            intro_templates.append('about_book')
        if self.book_metadata.about_author:
            intro_templates.append('about_author')

        # Adding 1 because we'll add a link to the first post of the chapter next
        book_intro_thread = self.build_status_from_templates(
            intro_templates,
            thread_count=len(intro_templates) + 1
        )
        # See if we have a cover image
        cover_immage, cover_description = self.get_book_image()
        if cover_immage and cover_description:
            book_intro_thread[0].media.append(RtMedia(file_path=cover_immage, description=cover_description))

        return book_intro_thread

    def create_chapter_thread(self) -> list[RtStatus]:
        # Go ahead and get the intro done
        chapter_thread = [self.render_daily_post(intro=True)]

        # Do chapter parts
        for i in range(len(self.chapter_paths)):
            chapter_thread.append(self._render_chapter_part(i))

        # Finish with the ending
        chapter_thread.append(self.render_daily_post(intro=False))

        return chapter_thread

    def create_link_to_chapter_thread(
            self, first_chapter_status: RtStatus, book_intro: RtStatus, thread_length: int
    ) -> RtStatus:
        extra_context = {
            'current_count': thread_length,
            'thread_count': thread_length,
            'first_chapter_link': first_chapter_status.url,
        }
        status = self.build_status_from_template('book_intro_link', extra_context)
        status.in_reply_to_id = book_intro.id
        return status

    def get_book_image(self) -> tuple[Path | None, str | None]:
        cover_path = self.working_directory / self.book_key / "cover.jpg"
        alt_path = self.working_directory / self.book_key / "cover.txt"

        if not cover_path.exists() or not alt_path.exists():
            return None, None

        return cover_path, open(str(alt_path), "r").read().strip()

    def build_status_from_templates(
            self,
            templates: list[str],
            extra_context: dict[str, Any]|None = None,
            thread_count: int = 0,
            count_offset: int = 0
    ) -> list[RtStatus]:
        if not extra_context:
            extra_context = {}
        if thread_count <= 0:
            thread_count = len(templates)
        extra_context['thread_count'] = thread_count
        statuses = []
        for i, template in enumerate(templates):
            extra_context['current_count'] = i + 1 + count_offset
            rendered_template = self.render_template(template, extra_context)
            statuses.append(RtStatus(text=rendered_template))

        return statuses

    def build_status_from_template(
            self,
            template: str,
            extra_context: dict[str, Any] | None = None,
    ) -> RtStatus:
        if not extra_context:
            extra_context = {}
        rendered_template = self.render_template(template, extra_context)
        return RtStatus(text=rendered_template)

    def render_daily_post(self, intro: bool=True) -> RtStatus:
        extra_context = {
            'thread_count': self._chapter_thread_count,
            'current_count': 1,
            'tomorrow': self.tomorrow,
            'next_book': self.next_book,
        }
        template = 'daily_intro'
        if not intro:
            if self.tomorrow:
                template = 'daily_ending'
            else:
                template = 'book_ending'
            extra_context['current_count'] = self._chapter_thread_count
        return self.build_status_from_template(template, extra_context=extra_context)

    def render_template(self, template_name: str, extra_context: dict[str, Any]|None=None) -> str:
        context = self._build_context(extra_context)
        template = self._load_template(template_name)
        rendered =  template.render(**context)
        return re.sub(r'(\n\s*)+\n+', '\n\n', rendered)

    def _build_context(self, extra_context: dict[str, Any] | None = None) -> dict[str, Any]:
        if extra_context is None:
            extra_context = {}

        greeter = Greeter(self.working_directory / 'resources' / 'word_choices.json')

        return {
            'book': self.book_metadata,
            'chapter': self.chapter_metadata,
            'greeting': greeter.greeting(),
            'sign_off': greeter.sign_off(),
            'english_sign_off': greeter.english_sign_off(),
            'tags': self.tags,
            'book_tags': self.book_tags,
            'bot_tags': self.bot_tags,
            'bot': self.bot_config
        } | extra_context

    @property
    def _chapter_thread_count(self) -> int:
        # total number of posts in the thread will be the length of the parts, + intro + ending
        return len(self.chapter_paths) + 2

    def _render_chapter_part(self, part_number: int) -> RtStatus:
        extra_context = {
            'first_content': part_number == 0,
            'current_count': 2 + part_number,
            'thread_count': self._chapter_thread_count,
            'content': self.chapter_paths[part_number].read_text()
        }
        spoiler_text = self.render_template("chapter_spoiler", extra_context=extra_context)
        status = self.build_status_from_template('chapter_text', extra_context=extra_context)
        status.spoiler_text = spoiler_text.strip()
        return status

    @property
    def book_tags(self) -> str:
        return self._get_tag_line(self.book_metadata.tags)

    @property
    def bot_tags(self):
        return self._get_tag_line(self.bot_config.tags)

    @property
    def tags(self):
        _book_tags = self.book_metadata.tags
        _bot_tags = self.bot_config.tags or []
        return self._get_tag_line(_book_tags + _bot_tags)

    def _get_tag_line(self, tag_list: list[str] | None) -> str:
        if not tag_list:
            return ''
        all_tags = [f"#{t}" for t in tag_list]
        return ' '.join(all_tags).strip()

    def _load_template(self, template_name: str) -> Template:
        possible_dir_name = self.template_base_dir / template_name
        template_path = f"{template_name}.txt"
        if possible_dir_name.exists():
            options = [f for f in possible_dir_name.iterdir()]
            option: Path = choice(options)
            template_path = f"{template_name}/{option.name}"
        return self.template_env.get_template(template_path)



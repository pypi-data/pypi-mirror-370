from pathlib import Path
from typing import Any

from _typeshed import Incomplete
from jinja2 import Template as Template
from robotooter.models.configs import BotConfig as BotConfig
from robotooter.models.statuses import RtStatus

from chapter_by_chapter.greeter import Greeter as Greeter
from chapter_by_chapter.models import BookMetadata as BookMetadata
from chapter_by_chapter.models import ChapterMetadata as ChapterMetadata

class ContentCreator:
    bot_config: Incomplete
    book_key: Incomplete
    book_metadata: Incomplete
    chapter_metadata: Incomplete
    chapter_paths: Incomplete
    working_directory: Incomplete
    tomorrow: Incomplete
    template_base_dir: Incomplete
    template_env: Incomplete
    def __init__(
        self,
        bot_config: BotConfig,
        book_metadata: BookMetadata,
        chapter_metadata: ChapterMetadata,
        chapter_paths: list[Path],
        working_directory: Path,
        tomorrow: ChapterMetadata | None
    ) -> None: ...
    def create_book_intro(self) -> list[RtStatus]: ...
    def create_chapter_thread(self) -> list[RtStatus]: ...
    def create_link_to_chapter_thread(
            self, first_chapter_status: RtStatus, book_intro: RtStatus, thread_length: int
    ) -> RtStatus: ...
    def get_book_image(self) -> tuple[Path | None, str | None]: ...
    def build_status_from_templates(self,
        templates: list[str],
        extra_context: dict[str, Any] | None = None,
        thread_count: int = 0,
        count_offset: int = 0
    ) -> list[RtStatus]: ...
    def build_status_from_template(self, template: str, extra_context: dict[str, Any] | None = None) -> RtStatus: ...
    def render_daily_post(self, intro: bool = True) -> RtStatus: ...
    def render_template(self, template_name: str, extra_context: dict[str, Any] | None = None) -> str: ...
    @property
    def book_tags(self) -> str: ...
    @property
    def bot_tags(self): ...
    @property
    def tags(self): ...

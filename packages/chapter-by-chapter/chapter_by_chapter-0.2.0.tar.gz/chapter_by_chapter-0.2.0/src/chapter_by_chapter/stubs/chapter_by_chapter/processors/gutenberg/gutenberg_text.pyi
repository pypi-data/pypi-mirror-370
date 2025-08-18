from pathlib import Path

from _typeshed import Incomplete

from chapter_by_chapter.models import BookMetadata as BookMetadata
from chapter_by_chapter.models import ChapterMetadata as ChapterMetadata
from chapter_by_chapter.processors.base_processor import BaseProcessor as BaseProcessor

RE_PART: Incomplete
RE_CHAPTER: Incomplete

class GutenbergTextProcessor(BaseProcessor):
    filters: Incomplete
    def __init__(self, book_key: str, output_dir: Path, file_path: Path, max_chunk_size: int) -> None: ...
    def process_file(self) -> None: ...

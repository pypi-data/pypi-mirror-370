from pathlib import Path

from _typeshed import Incomplete

from chapter_by_chapter.processors.gutenberg import GutenbergTextProcessor as GutenbergTextProcessor
from chapter_by_chapter.processors.gutenberg.gutenberg_html import GutenbergHtmlProcessor as GutenbergHtmlProcessor

RE_PART: Incomplete
RE_CHAPTER: Incomplete
MAX_CHUNK_SIZE: int

class Processor:
    output_dir: Incomplete
    def __init__(self, output_dir: Path) -> None: ...
    def process_url(self, book_key: str, url: str) -> None: ...
    def process_file(self, book_key: str, file_path: Path) -> None: ...

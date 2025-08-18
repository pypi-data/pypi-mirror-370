import abc
from abc import ABC, abstractmethod
from pathlib import Path

from _typeshed import Incomplete
from robotooter.filters.base_filter import BaseFilter as BaseFilter

class BaseProcessor(ABC, metaclass=abc.ABCMeta):
    book_key: Incomplete
    output_dir: Incomplete
    file_path: Incomplete
    max_chunk_size: Incomplete
    filters: list[BaseFilter]
    def __init__(self, book_key: str, output_dir: Path, file_path: Path, max_chunk_size: int) -> None: ...
    @abstractmethod
    def process_file(self) -> None: ...
    def chunk_chapter(self, book_key: str, chapter: int, text: list[str]) -> None: ...

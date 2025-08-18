from pytest_mock import MockerFixture as MockerFixture

from chapter_by_chapter import ChapterByChapterBot as ChapterByChapterBot
from chapter_by_chapter.greeter import Greeter as Greeter

def setup_test_bot(bot: ChapterByChapterBot, mocker: MockerFixture): ...

import shutil
from importlib import resources
from unittest.mock import PropertyMock

from pytest_mock import MockerFixture
from robotooter.mocks.fake_client import FakeClient

from chapter_by_chapter import ChapterByChapterBot
from chapter_by_chapter.greeter import Greeter


def setup_test_bot(bot: ChapterByChapterBot, mocker: MockerFixture):
    try:
        bot.install_package_resources()
    except Exception:
        pass # Depending on how the bot was created, these may already exist
    processed_path = resources.files('tests.testdata') / 'processing'
    working_dir = bot.working_directory / 'books'
    for book in ['a_study', 'frank']:
        shutil.copytree(str(processed_path / book), working_dir / book)
    # need to limit the choices in templates so they'll match
    template_dir = bot.resource_path('templates')
    dirs = ['book_ending', 'book_intro', 'daily_intro']
    for d in dirs:
        (template_dir / d / '2.txt').unlink()
        (template_dir / d / '3.txt').unlink()

    output_path = working_dir / 'output'
    output_path.mkdir(parents=True, exist_ok=True)
    fake_client = FakeClient(output_path)
    prop_mock = PropertyMock(return_value=fake_client)
    mocker.patch('robotooter.mastodon.manager.MastodonManager.client', new=prop_mock)

    mocker.patch.object(Greeter, 'greeting', return_value='hello')
    mocker.patch.object(Greeter, 'sign_off', return_value='bye')
    mocker.patch.object(Greeter, 'english_sign_off', return_value='so long')

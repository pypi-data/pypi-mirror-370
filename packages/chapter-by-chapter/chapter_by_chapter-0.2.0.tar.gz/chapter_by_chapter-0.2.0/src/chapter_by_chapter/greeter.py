import json
import random
from pathlib import Path


class Greeter:
    def __init__(self, word_file_path: Path):
        self.word_file_path = word_file_path
        self.world_file = json.loads(self.word_file_path.read_text())

        keys = [k for k in self.world_file.keys()]
        self.language = random.choice(keys)

    def greeting(self) -> str:
        return self._get_text("greeting")

    def sign_off(self) -> str:
        return self._get_text("sign_off")

    def english_sign_off(self) -> str:
        return str(random.choice(self.world_file['English']['sign_off'])['text'])

    def _get(self, choice: dict[str, str], key: str) -> str:
        if key not in choice:
            return ''
        return choice[key]

    def _get_text(self, which: str) -> str:
        options: list[dict[str, str]] = self.world_file[self.language][which]
        choice: dict[str, str] = random.choice(options)
        extra = [self._get(choice,"anglicized"), self._get(choice,"translation")]
        extra = [e for e in extra if e]
        parens = ''
        if extra:
            parens = '(' + (', '.join(extra).strip()) + ')'
        return f"{choice['text']} {parens}".strip()

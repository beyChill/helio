
from app.errors.custom_errors import CliErrors
from app.utils.constants import SITENAME
from app.utils.named_tuples import Streamer
from stardust.config.settings import get_setting


class CliValidations:

    site_slug: str
    site_name: str
    lowercase: str = "abcdefghijklmnopqrstuvwxyz"
    uppercase: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    letters: str = f"{lowercase}{uppercase}"
    digits: str = "0123456789"
    default_prompt = get_setting().CLI_PROMPT
    lowercase_digits: str = f"{lowercase}{digits}_"
    VALIDSITES: set[str] = {"cb", "mfc", "sc"}
    SORT_OPTIONS: dict[str, str] = {
        "name": "streamer_name",
        "date": "last_broadcast",
        "num": "recorded",
    }

    @classmethod
    def input(cls, line: str) -> list[str]:
        if not line.split():
            raise CliErrors(None, "input", "get Kandy cb")
        return line.split()

    @classmethod
    def name_chars(cls, name_: str) -> None:
        if not all(chars in cls.lowercase_digits for chars in name_):
            raise CliErrors(
                name_,
                "valid_chars",
                "Use lowercase letters, digits 0-9, and underscore ( _ ) in name",
            )

    @classmethod
    def change_prompt(cls, prompt:str) :
        try:
            if prompt not in cls.VALIDSITES:
                raise CliErrors(prompt, "site_prompt", f"valid sites for prompt {cls.VALIDSITES}")
            return prompt
        except CliErrors as e:
            print(e)

    @classmethod
    def has_cam_site(cls, prompt: str, rest: list) -> None:
        if prompt == cls.default_prompt and not rest:
            raise CliErrors(None, "no_site", f"sites {cls.VALIDSITES}")

    @classmethod
    def chk_prompt(cls, prompt: str) -> None:
        if prompt == cls.default_prompt:
            return None

        if prompt not in cls.VALIDSITES:
            raise CliErrors(prompt, "chars_prompt", f"sites {cls.VALIDSITES}")

        cls.site_slug = prompt

    @classmethod
    def chk_user_prompt(cls, prompt: str | list[str]) -> None:
        if not bool(prompt):
            return None

        prompt, *_ = prompt

        if not bool(prompt):
            raise CliErrors(None, "no_site", f"sites {cls.VALIDSITES}")

        if prompt not in cls.VALIDSITES:
            raise CliErrors(prompt, "site_prompt", f"sites {cls.VALIDSITES}")

        cls.site_slug = prompt

    @classmethod
    def slug_to_site(cls) -> None:
        cls.site_name = SITENAME.get(cls.site_slug, "")

    @classmethod
    def check_input(cls, line: str, prompt: str) -> Streamer:
        try:

            name_, *rest = cls.input(line)

            cls.name_chars(name_)
            cls.has_cam_site(prompt, rest)
            cls.chk_prompt(prompt)
            cls.chk_user_prompt(rest)
            cls.slug_to_site()

            return Streamer(name_, cls.site_slug, cls.site_name)
        except CliErrors as e:
            print(e)
            return Streamer(None, None, None)

    @classmethod
    def check_sort(cls, sort: str):
        if sort not in cls.SORT_OPTIONS:
            options = []
            for k, _ in cls.SORT_OPTIONS.items():
                options.append(k)

            raise CliErrors(None, "input_table", f"use one sort option: {options}")

    def input_table(self, line: str):
        if not bool(line.split()):
            raise CliErrors(None, "input_table", "num = number")
        return line.split()

    def check_table(self, line: str):
        try:
            sort, *_ = self.input_table(line)
            self.check_sort(sort)
            value = self.SORT_OPTIONS.get(sort)
            return value

        except CliErrors as e:
            print(e)
            return None

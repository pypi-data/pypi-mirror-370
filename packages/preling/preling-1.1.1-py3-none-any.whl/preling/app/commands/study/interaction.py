from dataclasses import dataclass
from typing import Callable

from prompt_toolkit import PromptSession
from rich.console import Console
from rich.text import Text

from preling.utils.console import clear_current_line, clear_previous

__all__ = [
    'ask',
    'ExtraOption',
]

OPTION_DELIMITER = ' | '


@dataclass
class ExtraOption:
    title: str
    action: Callable[[], None]


def normalize_key(text: str) -> str:
    """Normalize the key for case-insensitive comparison."""
    return text.lower()


def build_options(extra_options: list[ExtraOption]) -> tuple[list[list[Text]], dict[str, ExtraOption]]:
    """Build the list of option prompts and a mapping from option keys to their actions."""
    prompt = []
    mapping: dict[str, ExtraOption] = {}
    for option in extra_options:
        if not option.title:
            raise ValueError('Option title cannot be empty.')
        prefix, suffix = option.title[0], option.title[1:]
        key = normalize_key(prefix)
        if key in mapping:
            raise ValueError(f'Duplicate key for options: {key}')
        mapping[key] = option
        prompt.append([Text(prefix, style='bold'), Text(suffix)])
    return prompt, mapping


def ask(
        console: Console,
        prompt: Text,
        extra_options: list[ExtraOption],
        *,
        on_before_input: Callable[[], None] | None = None,
) -> str:
    """Prompt the user for input or to choose one of the extra options."""
    options_prompt, options_mapping = build_options(extra_options)
    console.print(prompt, end='')
    for option_prompt in options_prompt:
        console.print(Text(OPTION_DELIMITER, style='dim'), end='')
        console.print(*option_prompt, sep='', end='')
    console.print()
    if on_before_input:
        on_before_input()
        clear_current_line()  # Otherwise the input made during the operation will get displayed twice
    while True:
        response = PromptSession().prompt()
        if option := options_mapping.get(normalize_key(response)):
            clear_previous()
            option.action()
        else:
            return response.strip()

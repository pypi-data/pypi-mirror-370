from openai import OpenAI
from typing import Generator

from preling.db.models import Sentence

__all__ = [
    'explain',
]

TEMPERATURE = 0.0


def generate_prompt(language: str, sentence: Sentence) -> str:
    """Generate a prompt instructing the LLM to explain a sentence written in a given language."""
    return '\n'.join([
        f"Here is a sentence written in the language with code `{language}`:",
        f"",
        f"`{sentence.sentence}`",
        f"",
        f"Explain to the learner of the language what this sentence means and how it is constructed. "
        f"Do not mention the language code `{language}` in your explanation.",
    ])


def explain(sentence: Sentence, language: str, model: str, api_key: str) -> Generator[str, None, None]:
    """Stream an explanation for a sentence written in a specified language using the LLM."""
    for event in OpenAI(api_key=api_key).responses.create(
        model=model,
        temperature=TEMPERATURE,
        input=generate_prompt(language, sentence),
        stream=True,
    ):
        if event.type == 'response.output_text.delta':
            yield event.delta

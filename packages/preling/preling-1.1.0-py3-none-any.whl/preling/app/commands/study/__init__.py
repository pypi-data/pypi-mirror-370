from functools import partial
from typing import Annotated

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text
from typer import Argument, Option

from preling.app.app import app
from preling.db import get_session, Session
from preling.db.models import Sentence, Word
from preling.utils.console import clear_previous
from .chooser import choose_next
from .evaluator import evaluate, SentenceEvaluation, WordEvaluation
from .explainer import explain
from .interaction import ask, ExtraOption
from .tts import read
from .updater import update_sentence, update_word

__all__ = [
    'study',
]

SECTION_DELIMITER = Text('-' * 3, style='dim')

NEW_WORDS_SINGULAR = 'New word:'
NEW_WORDS_PLURAL = 'New words:'

AUDIO_ONLY_PROMPT = Text('(...)')

REPEAT_TITLE = 'Repeat'
EXPLAIN_TITLE = 'Explain'
QUIT_TITLE = 'Quit'

EVALUATION_IN_PROGRESS = Text('Evaluating translation...', style='dim')
ENTER_TO_CONTINUE = Text('Press Enter to continue...', style='dim')

YOURS = 'Yours:'
LLMS = "LLM's:"
BACK_TRANSLATION_DELIMITER = ' ~ '
CORRECT_MARK = '✅'
INCORRECT_MARK = '❌'
UNCLEAR_MARK = '❓'
LLM_MARK = '🔹'

CONSOLE = Console(highlight=False)

QUIT_OPTION = [ExtraOption(QUIT_TITLE, lambda: exit(0))]


def find_new_words(sentence: Sentence) -> dict[int, Word]:
    """Find words in a sentence that are not yet learned, indexed by their IDs."""
    return {word.id: word for word in sentence.words if word.due is None}


def print_new_words(words: dict[int, Word], target_word_id: int) -> None:
    """Print the new words found in a sentence, highlighting the target word."""
    CONSOLE.print(Text(NEW_WORDS_SINGULAR if len(words) == 1 else NEW_WORDS_PLURAL, style='yellow'))
    for word_id, word in sorted(words.items()):
        CONSOLE.print(
            Text(f'#{word_id}: ', style='red' if word_id == target_word_id else '')
            + Text(word.word.upper(), style='bold'),
        )
    CONSOLE.print(SECTION_DELIMITER)


def print_evaluation(translation: str, evaluation: SentenceEvaluation) -> None:
    """Print the evaluation results of a sentence translation."""
    CONSOLE.print(SECTION_DELIMITER)
    CONSOLE.print(' '.join([YOURS, CORRECT_MARK if evaluation.is_correct else INCORRECT_MARK, translation]), end='')
    if not evaluation.is_correct and evaluation.back_translation:
        CONSOLE.print(
            Text(BACK_TRANSLATION_DELIMITER, style='dim')
            + Text(evaluation.back_translation, style='bold'),
            end='',
        )
    CONSOLE.print()
    CONSOLE.print(' '.join([LLMS, LLM_MARK, evaluation.llm_translation]))
    CONSOLE.print(SECTION_DELIMITER)
    for e in evaluation.words:
        CONSOLE.print(
            Text(f'{CORRECT_MARK if e.is_correct else UNCLEAR_MARK if e.is_correct is None else INCORRECT_MARK} ')
            + Text(e.word, style='bold')
            + Text(f': {e.llm_translation}'),
        )


def update(sentence: Sentence, evaluation: SentenceEvaluation, session: Session) -> None:
    """Update the database with the results of the evaluation."""
    update_sentence(sentence, evaluation.is_correct)
    for e in evaluation.words:
        if e.is_correct is not None:
            update_word(e.word_data, e.is_correct)
    session.commit()


def build_explanation_option(sentence: Sentence, language: str, model: str, api_key: str) -> list[ExtraOption]:
    """Build an option to explain the sentence using the LLM."""
    def do_explain():
        chunks: list[str] = []
        with CONSOLE.screen():
            CONSOLE.print(sentence.sentence, style='bold red')
            CONSOLE.print()
            with Live(console=CONSOLE) as live:
                for chunk in explain(sentence, language, model, api_key):
                    chunks.append(chunk)
                    live.update(Markdown(''.join(chunks)))
            CONSOLE.print()
            CONSOLE.print(ENTER_TO_CONTINUE)
            input()

    return [ExtraOption(EXPLAIN_TITLE, do_explain)]


@app.command()
def study(
        model: Annotated[
            str,
            Option(
                '--model',
                envvar='PRELING_MODEL',
                help='GPT model for grammar evaluation.',
            ),
        ],
        tts_model: Annotated[
            str,
            Option(
                '--tts-model',
                envvar='PRELING_TTS_MODEL',
                help='Text‑to‑speech model.',
            ),
        ],
        api_key: Annotated[
            str,
            Option(
                '--api-key',
                envvar='PRELING_API_KEY',
                help='OpenAI API key.',
            ),
        ],
        language: Annotated[
            str,
            Argument(
                help='Language code previously initialised with `preling init`.',
            ),
        ],
        audio: Annotated[
            bool,
            Option(
                '--audio',
                help='Play audio in addition to printing text.',
            ),
        ] = False,
        audio_only: Annotated[
            bool,
            Option(
                '--audio-only',
                help='Play audio without displaying the text.',
            ),
        ] = False,
) -> None:
    """Launch an interactive study session."""
    with get_session(language) as session:
        target_word: Word
        sentence: Sentence

        def update_next() -> None:
            nonlocal target_word, sentence
            target_word, sentence = choose_next(session)

        update_next()

        while True:
            if new_words := find_new_words(sentence):
                print_new_words(new_words, target_word.id)
            formatted_sentence = Text(sentence.sentence, style='bold')

            do_read = partial(read, sentence.sentence, language, tts_model, api_key) if audio or audio_only else None
            repeat_option = [ExtraOption(REPEAT_TITLE, do_read)] if do_read else []

            translation = ask(
                CONSOLE,
                formatted_sentence if not audio_only else AUDIO_ONLY_PROMPT,
                repeat_option + QUIT_OPTION,
                on_before_input=do_read,
            )
            clear_previous(2)
            CONSOLE.print(formatted_sentence)
            CONSOLE.print(translation)
            CONSOLE.print(EVALUATION_IN_PROGRESS)
            evaluation = evaluate(sentence, language, translation, model, api_key)
            clear_previous()
            print_evaluation(translation, evaluation)
            update(sentence, evaluation, session)
            ask(
                CONSOLE,
                ENTER_TO_CONTINUE,
                repeat_option + build_explanation_option(sentence, language, model, api_key) + QUIT_OPTION,
                on_before_input=update_next,
            )
            clear_previous(2)
            CONSOLE.print(SECTION_DELIMITER)

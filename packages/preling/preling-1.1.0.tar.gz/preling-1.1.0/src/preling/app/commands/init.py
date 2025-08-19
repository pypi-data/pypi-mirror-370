from __future__ import annotations
from collections import Counter
from pathlib import Path
from typing import Annotated, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from spacy.language import Language
from tqdm import tqdm
from typer import Argument

from preling.app.app import app
from preling.db import get_session, Session
from preling.db.models import Sentence, SentenceWord, Word
from preling.utils.typer import typer_raise

__all__ = [
    'init',
]


def get_nlp(language: str) -> Language:
    """Get a spaCy language model for the specified language."""
    import spacy
    try:
        return spacy.blank(language)
    except ImportError:
        typer_raise(f'Language "{language}" is not supported by spaCy.')


def get_sentences(corpus: Path) -> Generator[str, None, None]:
    """Yield sentences from the corpus file."""
    with corpus.open('r', encoding='utf-8') as file:
        for line in file:
            if sentence := line.strip():
                yield sentence


def extract_words(nlp: Language, sentence: str) -> list[str]:
    """Extract words from a sentence using spaCy."""
    return [token.lower_ for token in nlp(sentence) if any(c.isalpha() for c in token.text)]


def process_corpus(language: str, corpus: Path) -> tuple[dict[str, list[str]], Counter[str]]:
    """Process the corpus and return words by sentence and word frequencies."""
    nlp = get_nlp(language)

    words_by_sentence: dict[str, list[str]] = {}
    word_frequencies: Counter[str] = Counter()

    for sentence in tqdm(get_sentences(corpus), desc=f'Processing sentences'):
        if sentence not in words_by_sentence and (words := extract_words(nlp, sentence)):
            words_by_sentence[sentence] = words
            word_frequencies.update(words)

    return words_by_sentence, word_frequencies


def add_words(session: Session, frequencies: Counter[str]) -> dict[str, int]:
    """Add words to the database and return a mapping of words to their IDs."""
    ids_by_word: dict[str, int] = {}
    for word, occurrences in tqdm(frequencies.most_common(), desc='Adding words'):
        word_obj = Word(
            word=word,
            occurrences=occurrences,
            streak_start=None,
            due=None,
        )
        session.add(word_obj)
        session.flush()
        ids_by_word[word] = word_obj.id
    return ids_by_word


def add_sentences(session: Session, words_by_sentence: dict[str, list[str]], ids_by_word: dict[str, int]) -> None:
    """Add sentences to the database."""
    for sentence_text, words in tqdm(words_by_sentence.items(), desc='Adding sentences'):
        sentence_obj = Sentence(
            sentence=sentence_text,
            correct_attempts=0,
            incorrect_attempts=0,
        )
        session.add(sentence_obj)
        session.flush()
        for word_index, word in enumerate(words):
            session.add(SentenceWord(
                sentence_id=sentence_obj.id,
                word_index=word_index,
                word_id=ids_by_word[word],
            ))
        session.flush()


@app.command()
def init(
        language: Annotated[
            str,
            Argument(help='Language code supported by spaCy (e.g., "en", "fr", "uk").'),
        ],
        corpus: Annotated[
            Path,
            Argument(
                dir_okay=False,
                exists=True,
                readable=True,
                resolve_path=True,
                help='Plain‑text file containing one sentence per line.',
            ),
        ],
) -> None:
    """Initialise PreLing for a new language."""
    with get_session(language) as session:
        if session.query(Sentence).first():
            typer_raise(f'PreLing is already initialized for language "{language}".')
        words_by_sentence, word_frequencies = process_corpus(language, corpus)
        if not word_frequencies:
            typer_raise(f'No valid sentences found in the corpus.')
        ids_by_word = add_words(session, word_frequencies)
        add_sentences(session, words_by_sentence, ids_by_word)
        print('Committing changes to the database...')
        session.commit()
    print(f'Initialized PreLing for language "{language}" '
          f'with {len(words_by_sentence)} unique sentences '
          f'and {len(word_frequencies)} unique words.')

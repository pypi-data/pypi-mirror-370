from collections.abc import Iterable
from functools import partial
from random import random
from typing import cast

from preling.db import Session
from preling.db.models import Sentence, SentenceWord, Word
from preling.utils.time import get_timestamp
from preling.utils.typer import typer_raise

__all__ = [
    'choose_next',
]

MAX_CANDIDATE_SENTENCES = 1000  # Maximum number of rows to scan when choosing a sentence


def choose_next_word(session: Session) -> Word:
    """
    Return the next word to learn or review, using the following priority:
    1. The word with the earliest `due` timestamp that is already due.
    2. If no such word exists, the most frequent unlearned word (i.e., the one with the smallest `id` and `due`==None).
    3. If no unlearned words remain, the word with the earliest future `due`.
    """
    if next_due_word := session.query(Word).filter(
        Word.due.is_not(None),
        Word.due <= get_timestamp(),
    ).order_by(Word.due).first():
        return cast(Word, next_due_word)
    if next_most_frequent_word := session.query(Word).filter(
        Word.due.is_(None),
    ).order_by(Word.id).first():
        return cast(Word, next_most_frequent_word)
    if next_due_word := session.query(Word).filter(
        Word.due.is_not(None),
    ).order_by(Word.due).first():
        return cast(Word, next_due_word)
    typer_raise('No words to learn or review found in the database.')


def make_sentence_key(now: int, sentence: Sentence) -> tuple[int, int, int, float]:
    """
    Compute a ranking key for `sentence`:
    - the number of unlearned words in the sentence;
    - the *negative* number of due words in the sentence (so that `min()` maximizes them);
    - the sum of ids of unlearned words in the sentence;
    - a random float for tie‑breaking.
    """
    unlearned_count = sum(1 for word in sentence.words if word.due is None)
    due = sum(1 for word in sentence.words if word.due is not None and word.due <= now)
    unlearned_ids_sum = sum(word.id for word in sentence.words if word.due is None)
    return unlearned_count, -due, unlearned_ids_sum, random()


def choose_next_sentence(session: Session, word: Word) -> Sentence:
    """
    Choose a sentence for `word`, limited to the first `MAX_CANDIDATE_SENTENCES` matches, optimizing for:
    1. Fewest unlearned words.
    2. Most words that are currently due.
    3. Randomness among ties.
    """
    return min(
        (cast(
            Iterable[Sentence],
            session.query(Sentence)
            .join(SentenceWord, Sentence.id == SentenceWord.sentence_id)
            .filter(SentenceWord.word_id == word.id)
            .order_by(SentenceWord.random_key)
            .limit(MAX_CANDIDATE_SENTENCES),
        )),
        key=partial(make_sentence_key, get_timestamp()),
    )


def choose_next(session: Session) -> tuple[Word, Sentence]:
    """Pick the next word and sentence to learn or review."""
    word = choose_next_word(session)
    sentence = choose_next_sentence(session, word)
    return word, sentence

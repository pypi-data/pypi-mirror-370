from datetime import timedelta

from preling.db.models import Sentence, Word
from preling.utils.time import get_timestamp

__all__ = [
    'update_sentence',
    'update_word',
]

INITIAL_INTERVAL = timedelta(hours=1)


def update_sentence(sentence: Sentence, is_correct: bool) -> None:
    """Update the sentence statistics based on whether the answer was correct."""
    if is_correct:
        sentence.correct_attempts += 1
    else:
        sentence.incorrect_attempts += 1


def update_word(word: Word, is_correct: bool) -> None:
    """Update spaced-repetition fields for a word depending on answer correctness."""
    now = get_timestamp()
    if is_correct:
        word.streak_start = word.streak_start or now
        word.due = now + max(now - word.streak_start, int(INITIAL_INTERVAL.total_seconds()))
    else:
        word.streak_start = None
        word.due = now

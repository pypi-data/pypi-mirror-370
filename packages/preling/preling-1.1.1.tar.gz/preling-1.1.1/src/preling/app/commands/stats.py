from __future__ import annotations
from typing import Annotated

from dataclasses import dataclass, field
from rich.console import Console
from rich.text import Text
from tqdm import tqdm
from typer import Argument

from preling.app.app import app
from preling.db import get_session, Session
from preling.db.models import Sentence, Word
from preling.utils.time import get_timestamp

__all__ = [
    'stats',
]


@dataclass
class WordStatsItem:
    count: int = 0
    occurrences: int = 0

    def add_word(self, word: Word) -> None:
        """Add a word to the stats item."""
        self.count += 1
        self.occurrences += word.occurrences

    def format(self, total: int) -> Text:
        """Format the word stats item for display."""
        return Text(f'{self.count} ') + Text(f'(coverage: {self.occurrences / max(total, 1):.1%})', style='dim')


@dataclass
class WordStats:
    active: WordStatsItem = field(default_factory=WordStatsItem)
    seen: WordStatsItem = field(default_factory=WordStatsItem)
    total: WordStatsItem = field(default_factory=WordStatsItem)


@dataclass
class SentenceStats:
    correct: int = 0
    seen: int = 0
    total_sentences: int = 0
    total_attempts: int = 0


def compute_word_stats(session: Session) -> WordStats:
    """Compute word statistics for the current language."""
    now = get_timestamp()
    word_stats = WordStats()
    word: Word
    for word in tqdm(session.query(Word).all(), desc='Computing word statistics', leave=False):
        word_stats.total.add_word(word)
        if word.due is not None:
            word_stats.seen.add_word(word)
            if word.due > now:
                word_stats.active.add_word(word)
    return word_stats


def compute_sentence_stats(session: Session) -> SentenceStats:
    """Compute sentence statistics for the current language."""
    sentence_stats = SentenceStats()
    for sentence in tqdm(session.query(Sentence).all(), desc='Computing sentence statistics', leave=False):
        if sentence.correct_attempts:
            sentence_stats.correct += 1
        if sentence.incorrect_attempts or sentence.correct_attempts:
            sentence_stats.seen += 1
        sentence_stats.total_sentences += 1
        sentence_stats.total_attempts += sentence.correct_attempts + sentence.incorrect_attempts
    return sentence_stats


def format_section_title(title: str) -> Text:
    """Format a section title for display."""
    return Text(title, style='bold underline')


def format_stats_label(title: str) -> Text:
    """Format a stats title for display."""
    return Text(f'{title}:', style='bold')


def print_word_stats(console: Console, word_stats: WordStats) -> None:
    """Print word statistics to the console."""
    total_occurrences = word_stats.total.occurrences
    console.print(format_section_title('Word Statistics'))
    console.print(format_stats_label('In retention'), word_stats.active.format(total_occurrences))
    console.print(format_stats_label('Seen words'), word_stats.seen.format(total_occurrences))
    console.print(format_stats_label('Total words'), word_stats.total.format(total_occurrences))


def print_sentence_stats(console: Console, sentence_stats: SentenceStats) -> None:
    """Print sentence statistics to the console."""
    console.print(format_section_title('Sentence Statistics'))
    console.print(format_stats_label('Correct at least once'), sentence_stats.correct)
    console.print(
        format_stats_label('Seen sentences'),
        sentence_stats.seen,
        Text(f'(out of {sentence_stats.total_sentences})', style='dim'),
    )
    console.print(format_stats_label('Total attempts'), sentence_stats.total_attempts)


@app.command()
def stats(
        language: Annotated[
            str,
            Argument(help='Language code to show study statistics for.'),
        ],
) -> None:
    """Display study statistics for the given language."""
    with get_session(language) as session:
        word_stats = compute_word_stats(session)
        sentence_stats = compute_sentence_stats(session)

    console = Console(highlight=False)
    print_word_stats(console, word_stats)
    console.print()
    print_sentence_stats(console, sentence_stats)

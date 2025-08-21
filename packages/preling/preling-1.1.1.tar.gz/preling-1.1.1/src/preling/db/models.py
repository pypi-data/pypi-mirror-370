from __future__ import annotations

from sqlalchemy import ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

__all__ = [
    'EvaluationCache',
    'Sentence',
    'SentenceWord',
    'Word',
]


class Sentence(Base):
    __tablename__ = 'sentences'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sentence: Mapped[str]
    correct_attempts: Mapped[int]
    incorrect_attempts: Mapped[int]

    words: Mapped[list[Word]] = relationship(
        'Word',
        secondary='sentence_word_index',
        order_by=lambda: SentenceWord.word_index,
        back_populates='sentences',
        passive_deletes=True,
    )


class Word(Base):
    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    word: Mapped[str]
    occurrences: Mapped[int]
    streak_start: Mapped[int | None]  # Unix timestamp
    due: Mapped[int | None]  # Unix timestamp

    sentences: Mapped[list[Sentence]] = relationship(
        'Sentence',
        secondary='sentence_word_index',
        order_by=lambda: SentenceWord.random_key,
        back_populates='words',
        passive_deletes=True,
    )


Index('ix_words_id_due_null', Word.id, sqlite_where=Word.due.is_(None))
Index('ix_words_due_due_not_null', Word.due, sqlite_where=Word.due.is_not(None))


class SentenceWord(Base):
    __tablename__ = 'sentence_word_index'

    sentence_id: Mapped[int] = mapped_column(
        ForeignKey(Sentence.id, ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
    )
    word_index: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(
        ForeignKey(Word.id, ondelete='CASCADE', onupdate='CASCADE'),
    )
    random_key: Mapped[int] = mapped_column(server_default=text('(abs(random()) % 16384)'))

    __table_args__ = (
        Index('ix_sentence_word_index_word_id_random_key', 'word_id', 'random_key'),
        {'sqlite_with_rowid': False},
    )


class EvaluationCache(Base):
    __tablename__ = 'evaluation_cache'

    sentence_id: Mapped[int] = mapped_column(
        ForeignKey(Sentence.id, ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
    )
    model: Mapped[str] = mapped_column(primary_key=True)
    translation: Mapped[str] = mapped_column(primary_key=True)
    evaluation: Mapped[str]

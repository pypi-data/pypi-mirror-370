from dataclasses import dataclass
import unicodedata

from openai import OpenAI
from pydantic import BaseModel

from preling.db import get_session
from preling.db.models import EvaluationCache, Sentence, Word

__all__ = [
    'evaluate',
    'SentenceEvaluation',
    'WordEvaluation',
]

TEMPERATURE = 0.0


@dataclass
class WordEvaluation:
    word: str
    word_data: Word
    is_correct: bool | None
    llm_translation: str


@dataclass
class SentenceEvaluation:
    is_correct: bool
    llm_translation: str
    back_translation: str | None
    words: list[WordEvaluation]


class WordOutput(BaseModel):
    word_number: int
    lowercased_word: str
    word: str
    llm_translation: str
    correctly_translated: bool | None


class SentenceOutput(BaseModel):
    llm_translation: str
    correctly_translated: bool
    back_translation: str | None
    words: list[WordOutput]


def normalize_spelling(word: str) -> str:
    return unicodedata.normalize('NFC', word.strip())


def generate_prompt(language: str, sentence: Sentence, translation: str) -> str:
    """
    Generate a prompt for the LLM to evaluate an English translation of a sentence
    from the specified source language.
    """
    return '\n'.join([
        f"A learner of the language with code `{language}` has attempted to translate "
        f"the following sentence from this language into English:",
        f"`{sentence.sentence}`",
        "Their translation is:",
        f"`{translation}`",
        "Determine whether the learner's translation is correct. Also, provide your own "
        "translation that you consider perfect. It may match the learner's version, or differ, "
        "even if you deem the learner's attempt correct but see room for minor improvements. "
        "If the learner's translation is incorrect, provide a back-translation of it into "
        "the original language.",
        "Additionally, here is the list of words in the sentence, in order (lowercased):",
        *[
            f"{word_number}) {word.word.lower()}"
            for word_number, word in enumerate(sentence.words, start=1)
        ],
        "For each word, provide the following information:",
        "- Your own translation of the word into English within the context of the sentence.",
        "- Whether the learner's translation of the word is correct—that is, whether all "
        "information conveyed by the word (lexical and/or grammatical) is present in the learner's "
        "translation. You may return null if it's unclear from the learner's translation whether "
        "they understood the word correctly.",
    ])


def build_evaluation(sentence_analysis: SentenceOutput, sentence: Sentence) -> SentenceEvaluation:
    """Build a `SentenceEvaluation` from the LLM's analysis of the sentence and its words."""
    return SentenceEvaluation(
        is_correct=sentence_analysis.correctly_translated,
        llm_translation=sentence_analysis.llm_translation,
        back_translation=sentence_analysis.back_translation,
        words=[
            WordEvaluation(
                word=word.word,
                word_data=sentence.words[word.word_number - 1],
                is_correct=word.correctly_translated,
                llm_translation=word.llm_translation,
            )
            for word in sentence_analysis.words
            if 1 <= word.word_number <= len(sentence.words)
            and (normalize_spelling(sentence.words[word.word_number - 1].word.lower()) ==
                 normalize_spelling(word.lowercased_word))
        ],
    )


def request(sentence: Sentence, language: str, translation: str, model: str, api_key: str) -> SentenceOutput:
    """Request the LLM to evaluate the translation of a sentence."""
    return OpenAI(api_key=api_key).responses.parse(
        model=model,
        temperature=TEMPERATURE,
        text_format=SentenceOutput,
        input=generate_prompt(language, sentence, translation),
    ).output_parsed


def cached_request(sentence: Sentence, language: str, translation: str, model: str, api_key: str) -> SentenceOutput:
    """Request the LLM to evaluate the translation of a sentence, using cache if available."""
    with get_session(language) as session:
        if cached := session.query(EvaluationCache).filter(
            EvaluationCache.sentence_id == sentence.id,
            EvaluationCache.model == model,
            EvaluationCache.translation == translation,
        ).first():
            return SentenceOutput.model_validate_json(cached.evaluation)
        else:
            output = request(sentence, language, translation, model, api_key)
            session.add(EvaluationCache(
                sentence_id=sentence.id,
                model=model,
                translation=translation,
                evaluation=output.model_dump_json(),
            ))
            return output


def evaluate(sentence: Sentence, language: str, translation: str, model: str, api_key: str) -> SentenceEvaluation:
    """Evaluate the translation of a sentence from the specified language into English using an LLM."""
    return build_evaluation(cached_request(sentence, language, translation, model, api_key), sentence)

import asyncio
from random import choice

from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

__all__ = [
    'read',
]

VOICES = [
    'alloy',
    'ash',
    'ballad',
    'coral',
    'echo',
    'fable',
    'nova',
    'onyx',
    'sage',
    'shimmer',
]

RESPONSE_FORMAT = 'pcm'


def read(text: str, language: str, model: str, api_key: str) -> None:
    """Read the given text using OpenAI's TTS service."""
    async def do_read() -> None:
        async with AsyncOpenAI(api_key=api_key) as client:
            async with client.audio.speech.with_streaming_response.create(
                    model=model,
                    voice=choice(VOICES),
                    input=text,
                    instructions=f'Language: {language}',
                    response_format=RESPONSE_FORMAT,
            ) as response:
                await LocalAudioPlayer().play(response)

    asyncio.run(do_read())

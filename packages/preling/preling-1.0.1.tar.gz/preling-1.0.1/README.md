# PreLing

PreLing is a command-line tool for improving language-comprehension skills through gradual exposure to new vocabulary. It supports every language that [SpaCy supports](https://spacy.io/usage/models#languages). Because PreLing uses GPT under the hood, you must have a paid [OpenAI account](https://platform.openai.com/) and an [API key](https://platform.openai.com/api-keys) to run it.

## Installation

Install [Python](https://www.python.org/downloads/) **3.12 or later** and [pipx](https://pipx.pypa.io/stable/installation/), then run:

```bash
pipx install preling          # install
pipx upgrade preling          # upgrade
pipx uninstall preling        # uninstall (hopefully you won't need this)
```

## Initialize a New Language

Prepare a plain-text file that contains **one sentence per line** in the language you want to learn. For example, you can download a monolingual corpus from [OPUS](https://opus.nlpl.eu/). Then run:

```bash
preling init <lang> <corpus>
```

`<lang>` is the [language code](https://spacy.io/usage/models#languages), and `<corpus>` is the path to the corpus file.

## Study a Language

```bash
preling study <lang> [--audio] [--audio-only] [--model <GPT_MODEL>] \
               [--tts-model <TTS_MODEL>] [--api-key <OPENAI_KEY>]
```

* **`<lang>`** – the language code you initialized earlier.
* **`--audio`** – play audio along with the text.  
* **`--audio-only`** – play audio without displaying the text.  
* **`--model`** – the GPT model to use for grammar evaluation.  
* **`--tts-model`** – the text-to-speech model to use for audio playback.  
* **`--api-key`** – your OpenAI API key.

Instead of passing these options each time, you can set the environment variables `PRELING_API_KEY`, `PRELING_MODEL`, and `PRELING_TTS_MODEL`.

## View Your Progress

```bash
preling stats <lang>
```

## Other Commands

```bash
preling path <lang>               # show the path to the language-data file
preling delete <lang> [--force]   # delete the language-data file; use --force to skip the confirmation prompt
```

# Suno to YouTube

Utilities to automate copying songs from [Suno](https://suno.ai/) to a YouTube channel.

The project currently provides simple tools to list songs on both platforms and
stores information about them in a local SQLite database. Authentication uses
environment variables `SUNO_API_KEY` and `YOUTUBE_API_KEY` or can be passed on
the command line.

## Setup

Install [uv](https://github.com/astral-sh/uv) and use it to create a virtual
environment and install the project:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

```
# List Suno songs
python -m suno_to_youtube.cli list-suno --api-key <YOUR_SUNO_TOKEN>

# Scrape songs from a public Suno profile using a browser (opens a visible window)
python -m suno_to_youtube.cli scrape-suno https://suno.com/@wavesoflove

# List YouTube videos from a channel
python -m suno_to_youtube.cli list-youtube <CHANNEL_ID> --api-key <YOUR_YT_KEY>
```

The commands store the song details in `suno_to_youtube.db`.

## VS Code Tasks

A set of VS Code tasks is provided in `.vscode/tasks.json` to simplify running
common commands. Use **Tasks: Run Task** from the command palette and select
one of the following:

- **Install dependencies** – install the project in editable mode using `uv`.
- **List Suno Songs** – list all songs using the Suno API.
- **List YouTube Videos** – list public videos from a channel.
- **Scrape Suno Profile** – scrape songs from a public profile in a browser.
- **Run Tests** – run the project's test suite with `pytest`.

The tasks prompt for API keys or other values when needed.

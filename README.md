# Suno to YouTube

Utilities to automate copying songs from [Suno](https://suno.ai/) to a YouTube channel.

The project currently provides simple tools to list songs on both platforms and
stores information about them in a local SQLite database. Authentication uses
environment variables `SUNO_API_KEY` and `YOUTUBE_API_KEY` or can be passed on
the command line.

## Usage

```
# List Suno songs
python -m suno_to_youtube.cli list-suno --api-key <YOUR_SUNO_TOKEN>

# List YouTube videos from a channel
python -m suno_to_youtube.cli list-youtube <CHANNEL_ID> --api-key <YOUR_YT_KEY>
```

The commands store the song details in `suno_to_youtube.db`.

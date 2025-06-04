"""Command line interface for the Suno to YouTube automation."""
from __future__ import annotations

import argparse
from typing import Iterable

from .database import Database, Song
from .suno_api import list_public_songs
from .youtube_api import list_channel_videos
from .browser import scrape_songs, ScrapedSong


def print_songs(songs: Iterable[Song]) -> None:
    for song in songs:
        print(f"{song.platform}:{song.platform_id} - {song.title}")


def cmd_list_suno(args: argparse.Namespace) -> None:
    db = Database()
    songs = list_public_songs(api_key=args.api_key)
    for suno_song in songs:
        song = Song(platform="suno", platform_id=suno_song.id, title=suno_song.title)
        db.add_song(song)
    print_songs(db.list_songs(platform="suno"))
    db.close()


def cmd_list_youtube(args: argparse.Namespace) -> None:
    db = Database()
    videos = list_channel_videos(args.channel_id, api_key=args.api_key)
    for video in videos:
        song = Song(platform="youtube", platform_id=video.id, title=video.title)
        db.add_song(song)
    print_songs(db.list_songs(platform="youtube"))
    db.close()


def cmd_scrape_suno(args: argparse.Namespace) -> None:
    """Scrape songs from a public Suno profile using a browser."""
    db = Database()
    scraped = scrape_songs(args.url)
    for item in scraped:
        # use the song URL as platform_id to ensure uniqueness
        song = Song(platform="suno", platform_id=item.url, title=item.title)
        db.add_song(song)
    print_songs(db.list_songs(platform="suno"))
    db.close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    suno_cmd = sub.add_parser("list-suno", help="List public Suno songs")
    suno_cmd.add_argument("--api-key", help="Suno API key")
    suno_cmd.set_defaults(func=cmd_list_suno)

    yt_cmd = sub.add_parser("list-youtube", help="List YouTube channel videos")
    yt_cmd.add_argument("channel_id", help="YouTube channel ID")
    yt_cmd.add_argument("--api-key", help="YouTube API key")
    yt_cmd.set_defaults(func=cmd_list_youtube)

    scrape_cmd = sub.add_parser("scrape-suno", help="Scrape songs from a Suno profile")
    scrape_cmd.add_argument("url", help="Profile URL, e.g. https://suno.com/@user")
    scrape_cmd.set_defaults(func=cmd_scrape_suno)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

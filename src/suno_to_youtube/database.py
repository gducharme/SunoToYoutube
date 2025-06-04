import sqlite3
from contextlib import closing
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class Song:
    platform: str  # e.g. "suno" or "youtube"
    platform_id: str
    title: str


def _create_tables(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                platform_id TEXT NOT NULL,
                title TEXT NOT NULL,
                UNIQUE(platform, platform_id)
            )
            """
        )


class Database:
    def __init__(self, path: str = "suno_to_youtube.db"):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        _create_tables(self.conn)

    def add_song(self, song: Song) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO songs (platform, platform_id, title) VALUES (?, ?, ?)",
                (song.platform, song.platform_id, song.title),
            )

    def list_songs(self, platform: Optional[str] = None) -> Iterable[Song]:
        cursor = self.conn.cursor()
        if platform:
            cursor.execute(
                "SELECT platform, platform_id, title FROM songs WHERE platform = ?",
                (platform,),
            )
        else:
            cursor.execute("SELECT platform, platform_id, title FROM songs")
        rows = cursor.fetchall()
        return [Song(*row) for row in rows]

    def close(self) -> None:
        self.conn.close()

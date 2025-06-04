"""Minimal wrapper around the Suno API.

This module exposes a function to list public songs. It requires a SUNO_API_KEY
environment variable or an explicit token to authenticate.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Optional

import requests


@dataclass
class SunoSong:
    id: str
    title: str
    url: str


def list_public_songs(api_key: Optional[str] = None) -> Iterable[SunoSong]:
    """Return a list of public songs for the authenticated user."""
    token = api_key or os.getenv("SUNO_API_KEY")
    if not token:
        raise ValueError("Suno API token not provided")

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get("https://studio-api.suno.ai/api/billing/feed", headers=headers)
    resp.raise_for_status()
    data = resp.json()
    songs = []
    for item in data.get("history", []):
        songs.append(
            SunoSong(
                id=item.get("id", ""),
                title=item.get("title", ""),
                url=item.get("audio_url", ""),
            )
        )
    return songs

"""Utilities for interacting with the YouTube Data API."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Optional

from googleapiclient.discovery import build


@dataclass
class YouTubeVideo:
    id: str
    title: str


def list_channel_videos(channel_id: str, api_key: Optional[str] = None) -> Iterable[YouTubeVideo]:
    """List public videos for a channel."""
    key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise ValueError("YouTube API key not provided")

    youtube = build("youtube", "v3", developerKey=key)
    videos = []
    request = youtube.search().list(part="id,snippet", channelId=channel_id, maxResults=50, type="video")
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            videos.append(
                YouTubeVideo(
                    id=item["id"]["videoId"],
                    title=item["snippet"]["title"],
                )
            )
        request = youtube.search().list_next(request, response)
    return videos

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

# Importing Playwright inside the function so that the module can be imported
# even if Playwright is not installed. This avoids ImportError when running
# commands that do not require the browser.

@dataclass
class ScrapedSong:
    """Simple representation of a song scraped from a Suno profile."""

    title: str
    url: str


def scrape_songs(profile_url: str) -> Iterable[ScrapedSong]:
    """Open a browser and return all songs found on the profile page.

    The previous implementation scrolled once to the bottom of the page and
    then scraped all anchors. On pages with infinite scrolling this could miss
    songs because new entries are only loaded when the page is scrolled further
    down.  The updated logic keeps scrolling and capturing song links until no
    new ones are discovered.
    """
    from playwright.sync_api import sync_playwright

    songs: dict[str, ScrapedSong] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(profile_url)

        # Repeatedly scroll down and capture new songs until none appear.
        prev_count = 0
        while True:
            # Query all song links currently loaded
            anchors = page.query_selector_all("a[href*='/song/']")
            for a in anchors:
                href = a.get_attribute("href") or ""
                title = a.inner_text().strip()
                if href and title and href not in songs:
                    songs[href] = ScrapedSong(title=title, url=href)

            # Scroll a page down to trigger loading more songs
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            page.wait_for_timeout(1000)

            if len(songs) == prev_count:
                break
            prev_count = len(songs)

        # Convert dict of songs to a list for deterministic return order
        song_list = list(songs.values())

        browser.close()
    return song_list

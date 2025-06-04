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
    """Open a browser, scroll the page and return the discovered songs."""
    from playwright.sync_api import sync_playwright

    songs: list[ScrapedSong] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(profile_url)

        # Scroll down until the page height no longer changes
        prev_height = 0
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            height = page.evaluate("document.body.scrollHeight")
            if height == prev_height:
                break
            prev_height = height

        # Extract song titles and URLs. The selectors may need to be updated if
        # Suno changes their markup.
        anchors = page.query_selector_all("a[href*='/song/']")
        for a in anchors:
            href = a.get_attribute("href") or ""
            title = a.inner_text().strip()
            if href and title:
                songs.append(ScrapedSong(title=title, url=href))

        browser.close()
    return songs

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from pathlib import Path

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
    screenshots = Path("screenshots")
    screenshots.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(profile_url)

        # Make sure the songs pane is focused. Clicking the "Songs" tab ensures
        # that PageDown events scroll the list of songs instead of another
        # region on the page.
        songs_tab = page.query_selector("text=Songs")
        if songs_tab:
            songs_tab.click()

        # Repeatedly scroll down and capture new songs until none appear.  Keep
        # track of the document height so we can detect when no new content is
        # loaded after sending the PageDown key.
        prev_count = 0
        prev_height = page.evaluate("document.body.scrollHeight")
        loop_count = 0
        while True:
            loop_count += 1
            # Query all song links currently loaded
            anchors = page.query_selector_all("a[href*='/song/']")
            for a in anchors:
                href = a.get_attribute("href") or ""
                title = a.inner_text().strip()
                if href and title and href not in songs:
                    songs[href] = ScrapedSong(title=title, url=href)

            # Save a screenshot for debugging. Having loop count in the file name
            # makes it easy to trace the progression during scraping.
            page.screenshot(path=str(screenshots / f"{loop_count}_capture.png"))

            # TODO: Waiting for a DOM mutation or network idle could provide a
            # more robust signal that new songs have loaded instead of the fixed
            # timeout used here.

            # Scroll down one page and wait for the document height to change.
            # If the height and song count remain the same, no new songs were
            # loaded and we are done.
            page.keyboard.press("PageDown")
            # Wait for the newly scrolled content to load. A longer delay
            # reduces the chance of missing songs on slower connections.
            page.wait_for_timeout(5000)
            height = page.evaluate("document.body.scrollHeight")
            if height == prev_height and len(songs) == prev_count:
                break
            prev_height = height
            prev_count = len(songs)

        # Convert dict of songs to a list for deterministic return order
        song_list = list(songs.values())

        browser.close()
    return song_list

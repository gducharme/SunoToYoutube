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


class _Scraper:
    """Helper implementing the scraping logic using smaller methods."""

    def __init__(self, profile_url: str) -> None:
        self.profile_url = profile_url
        self.songs: dict[str, ScrapedSong] = {}
        self.screenshots = Path("screenshots")
        self.screenshots.mkdir(exist_ok=True)

    # --- page helpers -------------------------------------------------
    def _open_page(self, p):
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(self.profile_url)
        self._focus_song_list(page)
        return browser, page

    def _focus_song_list(self, page) -> None:
        """Ensure the list of songs is active and loaded."""
        songs_tab = page.query_selector("text=Songs")
        if songs_tab:
            songs_tab.click()
            try:
                page.wait_for_selector("a[href*='/song/']", timeout=10000)
            except Exception:
                page.wait_for_timeout(3000)

    def _capture_current_songs(self, page) -> None:
        anchors = page.query_selector_all("a[href*='/song/']")
        for a in anchors:
            href = a.get_attribute("href") or ""
            title = a.inner_text().strip()
            if href and title and href not in self.songs:
                self.songs[href] = ScrapedSong(title=title, url=href)

    def _scroll_and_wait(self, page):
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        page.wait_for_load_state("networkidle")
        return page.evaluate("document.body.scrollHeight")

    # --- main entry ----------------------------------------------------
    def run(self) -> list[ScrapedSong]:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser, page = self._open_page(p)

            prev_count = 0
            prev_height = page.evaluate("document.body.scrollHeight")
            loop_count = 0

            while True:
                loop_count += 1
                self._capture_current_songs(page)
                page.screenshot(path=str(self.screenshots / f"{loop_count}_capture.png"))
                height = self._scroll_and_wait(page)
                if height == prev_height and len(self.songs) == prev_count:
                    break
                prev_height = height
                prev_count = len(self.songs)

            browser.close()
        return list(self.songs.values())


def scrape_songs(profile_url: str) -> Iterable[ScrapedSong]:
    """Open a browser and return all songs found on the profile page."""
    scraper = _Scraper(profile_url)
    return scraper.run()

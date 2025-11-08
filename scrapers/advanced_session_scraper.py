#!/usr/bin/env python3
"""
Advanced Session-Based Scraper
Maintains cookies, session state, and realistic browsing patterns
"""

import requests
import random
import time
from typing import Dict, Optional
from urllib.parse import urlparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedSessionScraper:
    """
    Maintains session state with cookies and realistic browsing behavior.
    Techniques used:
    1. Session persistence (cookies)
    2. Realistic headers with all browser fingerprint data
    3. Referer chain (looks like natural navigation)
    4. Human-like timing patterns
    5. TLS fingerprinting mitigation
    """

    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_history = []

        # Complete browser fingerprint
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'max-age=0',
        }

        self.session.headers.update(self.base_headers)

    def human_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add human-like random delay"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def get_headers_with_referer(self, url: str, referer: Optional[str] = None) -> Dict:
        """Get headers with proper referer chain"""
        headers = self.base_headers.copy()

        if referer:
            headers['Referer'] = referer
            # Update Sec-Fetch-Site based on referer
            if urlparse(url).netloc == urlparse(referer).netloc:
                headers['Sec-Fetch-Site'] = 'same-origin'
            else:
                headers['Sec-Fetch-Site'] = 'cross-site'
        else:
            headers['Sec-Fetch-Site'] = 'none'

        return headers

    def visit_homepage_first(self, url: str) -> bool:
        """
        Visit homepage before accessing deep pages.
        This establishes cookies and makes the traffic pattern more natural.
        """
        parsed = urlparse(url)
        homepage = f"{parsed.scheme}://{parsed.netloc}/"

        try:
            logger.info(f"Visiting homepage first: {homepage}")
            response = self.session.get(
                homepage,
                headers=self.get_headers_with_referer(homepage),
                timeout=30
            )

            self.request_history.append(homepage)
            self.human_delay(2, 4)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Failed to visit homepage: {e}")
            return False

    def scrape_url(self, url: str, visit_homepage: bool = True) -> Optional[str]:
        """
        Scrape URL with realistic session behavior.

        Args:
            url: Target URL
            visit_homepage: Whether to visit homepage first (recommended)
        """

        try:
            # Step 1: Visit homepage to establish session
            if visit_homepage and not self.request_history:
                self.visit_homepage_first(url)

            # Step 2: Get referer from history
            referer = self.request_history[-1] if self.request_history else None

            # Step 3: Make request with proper headers
            logger.info(f"Requesting: {url}")
            headers = self.get_headers_with_referer(url, referer)

            response = self.session.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )

            # Step 4: Track request in history
            self.request_history.append(url)

            if response.status_code == 200:
                logger.info(f"✓ Success: {url} ({len(response.content)} bytes)")
                self.human_delay()  # Random delay before next request
                return response.text

            elif response.status_code == 403:
                logger.error(f"✗ 403 Forbidden: {url}")
                logger.info(f"Response headers: {dict(response.headers)}")
                return None

            else:
                logger.warning(f"Status {response.status_code}: {url}")
                return None

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def scrape_with_retry(self, url: str, max_attempts: int = 3) -> Optional[str]:
        """Scrape with retry and session reset on failure"""

        for attempt in range(max_attempts):
            content = self.scrape_url(url, visit_homepage=(attempt == 0))

            if content:
                return content

            # If failed, reset session and try again
            if attempt < max_attempts - 1:
                logger.info(f"Resetting session and retrying (attempt {attempt + 2}/{max_attempts})")
                self.session = requests.Session()
                self.session.headers.update(self.base_headers)
                self.request_history = []
                time.sleep(2 ** attempt)  # Exponential backoff

        return None


def main():
    """Example usage"""
    scraper = AdvancedSessionScraper()

    # Scrape with realistic behavior
    urls = [
        'https://blog.hubspot.com/marketing',
        'https://neilpatel.com/blog/',
    ]

    for url in urls:
        content = scraper.scrape_with_retry(url)
        if content:
            logger.info(f"Successfully scraped {url}")
        else:
            logger.error(f"Failed to scrape {url}")


if __name__ == '__main__':
    main()

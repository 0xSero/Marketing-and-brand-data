#!/usr/bin/env python3
"""
Proxy Rotation Scraper
Rotates through multiple proxies to avoid IP-based 403 blocking
"""

import requests
import random
import time
from typing import List, Dict, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProxyRotationScraper:
    """
    Scrapes using rotating proxies to bypass IP-based blocking.

    You can use:
    1. Free proxy lists (unreliable)
    2. Paid proxy services (ScraperAPI, Bright Data, Oxylabs)
    3. Residential proxies (most effective but expensive)
    4. Your own proxy pool
    """

    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies or []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        ]
        self.current_proxy_index = 0

    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy from pool"""
        if not self.proxies:
            return None

        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy

    def get_headers(self) -> Dict:
        """Generate realistic headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    def scrape_url(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Scrape URL with proxy rotation"""

        for attempt in range(max_retries):
            try:
                # Get proxy
                proxy = self.get_next_proxy()
                proxies = None

                if proxy:
                    proxies = {
                        'http': proxy,
                        'https': proxy,
                    }
                    logger.info(f"Using proxy: {proxy}")

                # Make request
                response = requests.get(
                    url,
                    headers=self.get_headers(),
                    proxies=proxies,
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code == 200:
                    logger.info(f"✓ Success: {url}")
                    return response.text
                elif response.status_code == 403:
                    logger.warning(f"403 on attempt {attempt + 1} with proxy {proxy}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.warning(f"Status {response.status_code} on attempt {attempt + 1}")

            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                time.sleep(2 ** attempt)

        logger.error(f"✗ Failed after {max_retries} attempts: {url}")
        return None

    def add_free_proxies(self):
        """
        Add free proxies from public sources.
        Note: Free proxies are often slow and unreliable.
        """
        logger.info("Fetching free proxies...")

        try:
            # Free proxy list API
            response = requests.get(
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                timeout=10
            )

            if response.status_code == 200:
                proxies = response.text.strip().split('\r\n')
                self.proxies = [f'http://{p}' for p in proxies[:20]]  # Use first 20
                logger.info(f"Added {len(self.proxies)} free proxies")

        except Exception as e:
            logger.error(f"Failed to fetch free proxies: {e}")

    def use_scraper_api(self, api_key: str, url: str) -> Optional[str]:
        """
        Use ScraperAPI service (paid but very effective).
        Sign up at: https://www.scraperapi.com/
        """
        try:
            response = requests.get(
                'http://api.scraperapi.com/',
                params={
                    'api_key': api_key,
                    'url': url,
                    'render': 'true',  # Enable JavaScript rendering
                },
                timeout=60
            )

            if response.status_code == 200:
                return response.text

        except Exception as e:
            logger.error(f"ScraperAPI error: {e}")

        return None


def main():
    """Example usage"""

    # Option 1: Use your own proxies
    scraper = ProxyRotationScraper(proxies=[
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080',
    ])

    # Option 2: Use free proxies (unreliable)
    # scraper = ProxyRotationScraper()
    # scraper.add_free_proxies()

    # Option 3: Use ScraperAPI (paid service - most reliable)
    # api_key = 'your_api_key_here'
    # content = scraper.use_scraper_api(api_key, 'https://blog.hubspot.com')

    # Test scrape
    url = 'https://blog.hubspot.com/marketing'
    content = scraper.scrape_url(url)

    if content:
        logger.info(f"Scraped {len(content)} bytes")


if __name__ == '__main__':
    main()

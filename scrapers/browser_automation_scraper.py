#!/usr/bin/env python3
"""
Browser Automation Scraper using Playwright
Bypasses 403 by acting like a real browser with JavaScript execution
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrowserAutomationScraper:
    """
    Uses Playwright to scrape content like a real browser.
    Most effective against 403 blocks since it executes JavaScript
    and has complete browser fingerprint.
    """

    def __init__(self, headless: bool = True, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo  # Slow down operations in ms to appear more human

    async def scrape_url(self, url: str, wait_for: str = None) -> Dict:
        """Scrape a URL using real browser automation"""

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install")
            return None

        async with async_playwright() as p:
            # Launch browser with realistic settings
            browser = await p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=[
                    '--disable-blink-features=AutomationControlled',  # Hide automation
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )

            # Create context with realistic user agent and viewport
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'longitude': -74.0060, 'latitude': 40.7128},
                permissions=['geolocation'],
            )

            # Add extra headers
            await context.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })

            page = await context.new_page()

            # Hide webdriver property
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            logger.info(f"Loading: {url}")

            try:
                # Navigate to page
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)

                # Wait for specific element if provided
                if wait_for:
                    await page.wait_for_selector(wait_for, timeout=10000)
                else:
                    # Default wait for network to be idle
                    await page.wait_for_load_state('networkidle', timeout=10000)

                # Random human-like delay
                await asyncio.sleep(1)

                # Get page content
                title = await page.title()
                content = await page.content()
                text_content = await page.evaluate('() => document.body.innerText')

                logger.info(f"✓ Successfully scraped: {title}")

                await browser.close()

                return {
                    'url': url,
                    'title': title,
                    'html': content,
                    'text': text_content,
                    'word_count': len(text_content.split()),
                }

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                await browser.close()
                return None

    async def scrape_urls(self, urls: List[str], output_file: str = 'data/browser_scraped.jsonl'):
        """Scrape multiple URLs"""

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        successful = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            logger.info(f"[{i}/{len(urls)}] Processing: {url}")

            result = await self.scrape_url(url)

            if result:
                # Save to JSONL
                with open(output_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(result, ensure_ascii=False) + '\n')
                successful += 1
            else:
                failed += 1

            # Human-like delay between requests
            await asyncio.sleep(2)

        logger.info(f"\n{'='*80}")
        logger.info(f"Scraping complete: {successful} successful, {failed} failed")
        logger.info(f"{'='*80}")

        return successful, failed


async def main():
    # Example: Scrape marketing blog posts
    urls = [
        'https://blog.hubspot.com/marketing',
        'https://neilpatel.com/blog/',
        'https://moz.com/blog',
        'https://contentmarketinginstitute.com/articles/',
    ]

    scraper = BrowserAutomationScraper(headless=True, slow_mo=100)
    await scraper.scrape_urls(urls)


if __name__ == '__main__':
    asyncio.run(main())

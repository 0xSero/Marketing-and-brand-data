"""
Advanced Web Scraper with 403 Bypass
Uses multiple techniques to bypass bot protection and 403 errors.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedWebScraper:
    """Advanced scraper with 403 bypass capabilities"""

    def __init__(self, rate_limit=2.0):
        self.rate_limit = rate_limit
        self.session = requests.Session()

        # Rotating user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]

    def get_headers(self, referer=None):
        """Generate realistic browser headers"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        if referer:
            headers['Referer'] = referer

        return headers

    def fetch_with_retry(self, url: str, max_retries=3) -> Optional[requests.Response]:
        """Fetch URL with multiple retry strategies"""

        for attempt in range(max_retries):
            try:
                # Sleep to respect rate limits
                time.sleep(self.rate_limit + random.uniform(0, 1))

                # Try different strategies on each attempt
                if attempt == 0:
                    # Strategy 1: Normal request with good headers
                    response = self.session.get(
                        url,
                        headers=self.get_headers(),
                        timeout=30,
                        allow_redirects=True
                    )

                elif attempt == 1:
                    # Strategy 2: New session + referer
                    self.session = requests.Session()  # Fresh session
                    parsed = urlparse(url)
                    referer = f"{parsed.scheme}://{parsed.netloc}"

                    response = self.session.get(
                        url,
                        headers=self.get_headers(referer=referer),
                        timeout=30,
                        allow_redirects=True
                    )

                else:
                    # Strategy 3: Even longer wait + cookies
                    time.sleep(3)
                    self.session.cookies.clear()

                    response = self.session.get(
                        url,
                        headers=self.get_headers(),
                        timeout=30,
                        allow_redirects=True
                    )

                # Check if successful
                if response.status_code == 200:
                    logger.info(f"✓ Success: {url[:80]}")
                    return response
                elif response.status_code == 403:
                    logger.warning(f"403 on attempt {attempt + 1}: {url[:80]}")
                elif response.status_code == 429:
                    logger.warning(f"Rate limited, waiting longer...")
                    time.sleep(10)
                else:
                    logger.warning(f"Status {response.status_code}: {url[:80]}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")

        logger.error(f"Failed after {max_retries} attempts: {url[:80]}")
        return None

    def scrape_page(self, url: str) -> Optional[Dict]:
        """Scrape a single page"""
        response = self.fetch_with_retry(url)

        if not response:
            return None

        try:
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract title
            title = ""
            if soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            elif soup.find('title'):
                title = soup.find('title').get_text(strip=True)

            # Extract main content
            content = ""

            # Try common content containers
            for selector in ['article', 'main', '.post-content', '.entry-content', '.content', 'body']:
                element = soup.select_one(selector)
                if element:
                    # Remove unwanted elements
                    for unwanted in element.select('script, style, nav, header, footer, aside, .sidebar, .menu'):
                        unwanted.decompose()

                    content = element.get_text(separator='\n', strip=True)
                    if len(content) > 500:  # Good content found
                        break

            if not content or len(content) < 100:
                return None

            # Extract metadata
            meta_desc = ""
            meta_keywords = ""

            if soup.find('meta', {'name': 'description'}):
                meta_desc = soup.find('meta', {'name': 'description'}).get('content', '')

            if soup.find('meta', {'name': 'keywords'}):
                meta_keywords = soup.find('meta', {'name': 'keywords'}).get('content', '')

            return {
                'url': url,
                'title': title,
                'content': content[:10000],  # Limit size
                'meta_description': meta_desc,
                'meta_keywords': meta_keywords,
                'word_count': len(content.split()),
                'source': urlparse(url).netloc,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"Parsing error for {url}: {e}")
            return None

    def scrape_urls(self, urls: List[str], output_file='data/real_marketing_content.jsonl'):
        """Scrape multiple URLs"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        successful = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            logger.info(f"\n[{i}/{len(urls)}] Scraping: {url[:80]}")

            data = self.scrape_page(url)

            if data:
                # Save to JSONL
                with open(output_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')

                successful += 1
                logger.info(f"  Saved: {data['title'][:60]}... ({data['word_count']} words)")
            else:
                failed += 1

            # Progress update
            if i % 10 == 0:
                logger.info(f"\nProgress: {successful} successful, {failed} failed")

        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping complete!")
        logger.info(f"Successful: {successful}, Failed: {failed}")
        logger.info(f"{'='*60}")

        return successful, failed


if __name__ == '__main__':
    # Test URLs
    test_urls = [
        'https://moz.com/beginners-guide-to-seo',
        'https://contentmarketinginstitute.com/articles/content-marketing-framework/',
    ]

    scraper = AdvancedWebScraper(rate_limit=2)
    scraper.scrape_urls(test_urls)

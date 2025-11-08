"""
Base Scraper Class
Provides common functionality for all scrapers with ethical scraping practices.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import logging
from datetime import datetime

class BaseScraper:
    """
    Base class for all web scrapers with built-in ethical scraping practices.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        output_dir: str = "data/raw",
        rate_limit: float = 2.0,
        max_retries: int = 3,
        timeout: int = 30,
        respect_robots_txt: bool = True
    ):
        """
        Initialize the base scraper.

        Args:
            name: Name of the scraper
            base_url: Base URL of the website
            output_dir: Directory to save scraped data
            rate_limit: Delay between requests in seconds
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            respect_robots_txt: Whether to respect robots.txt (default: True)
        """
        self.name = name
        self.base_url = base_url
        self.output_dir = Path(output_dir) / name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self.respect_robots_txt = respect_robots_txt

        # Setup logging
        self.logger = logging.getLogger(f"scraper.{name}")

        # Track scraped URLs to avoid duplicates
        self.scraped_urls = set()
        self.load_progress()

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MarketingKnowledgeBot/1.0; +https://github.com/yourusername/marketing-knowledge-db)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Robots.txt parser
        self.robot_parser = None
        if self.respect_robots_txt:
            self.robot_parser = RobotFileParser()
            self.robot_parser.set_url(urljoin(base_url, '/robots.txt'))
            try:
                self.robot_parser.read()
                self.logger.info(f"Loaded robots.txt from {base_url}")
            except Exception as e:
                self.logger.warning(f"Could not load robots.txt: {e}")
        else:
            self.logger.info(f"Robots.txt checking disabled for {name} (non-commercial research use)")

        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'total_size_bytes': 0,
            'start_time': datetime.now().isoformat()
        }

    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        if not self.respect_robots_txt:
            return True  # Bypass robots.txt checking
        try:
            return self.robot_parser.can_fetch("*", url)
        except:
            return True  # If robots.txt parsing fails, allow fetching

    def get_url_hash(self, url: str) -> str:
        """Generate a unique hash for a URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def is_scraped(self, url: str) -> bool:
        """Check if URL has already been scraped"""
        return self.get_url_hash(url) in self.scraped_urls

    def mark_scraped(self, url: str):
        """Mark URL as scraped"""
        self.scraped_urls.add(self.get_url_hash(url))
        self.save_progress()

    def load_progress(self):
        """Load previously scraped URLs"""
        progress_file = self.output_dir / 'progress.json'
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                data = json.load(f)
                self.scraped_urls = set(data.get('scraped_urls', []))
                self.logger.info(f"Loaded {len(self.scraped_urls)} previously scraped URLs")

    def save_progress(self):
        """Save scraping progress"""
        progress_file = self.output_dir / 'progress.json'
        with open(progress_file, 'w') as f:
            json.dump({
                'scraped_urls': list(self.scraped_urls),
                'last_updated': datetime.now().isoformat(),
                'stats': self.stats
            }, f, indent=2)

    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """
        Fetch a page with retry logic and rate limiting.

        Args:
            url: URL to fetch

        Returns:
            Response object or None if failed
        """
        if not self.can_fetch(url):
            self.logger.warning(f"Robots.txt disallows fetching: {url}")
            return None

        if self.is_scraped(url):
            self.logger.info(f"Already scraped: {url}")
            return None

        for attempt in range(self.max_retries):
            try:
                self.stats['total_requests'] += 1
                time.sleep(self.rate_limit)  # Rate limiting

                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                self.logger.info(f"Successfully fetched: {url}")
                return response

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch after {self.max_retries} attempts: {url}")
                    self.stats['failed_scrapes'] += 1
                    return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup"""
        return BeautifulSoup(html, 'lxml')

    def extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Extract text from HTML using CSS selector"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""

    def extract_all_text(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Extract all text elements matching selector"""
        elements = soup.select(selector)
        return [el.get_text(strip=True) for el in elements]

    def save_json(self, data: Dict[str, Any], filename: str):
        """Save data as JSON"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Update stats
        size = filepath.stat().st_size
        self.stats['total_size_bytes'] += size
        self.stats['successful_scrapes'] += 1

        self.logger.info(f"Saved: {filepath} ({size} bytes)")

    def save_text(self, content: str, filename: str):
        """Save content as text file"""
        filepath = self.output_dir / f"{filename}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Update stats
        size = filepath.stat().st_size
        self.stats['total_size_bytes'] += size
        self.stats['successful_scrapes'] += 1

        self.logger.info(f"Saved: {filepath} ({size} bytes)")

    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """Extract common metadata from a page"""
        metadata = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'title': '',
            'description': '',
            'keywords': '',
            'author': '',
            'published_date': '',
            'og_image': ''
        }

        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)

        # Meta tags
        meta_tags = {
            'description': ['name', 'description'],
            'keywords': ['name', 'keywords'],
            'author': ['name', 'author'],
            'published_date': ['property', 'article:published_time'],
            'og_image': ['property', 'og:image']
        }

        for key, (attr, value) in meta_tags.items():
            tag = soup.find('meta', {attr: value})
            if tag:
                metadata[key] = tag.get('content', '')

        return metadata

    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        self.stats['total_size_mb'] = round(self.stats['total_size_bytes'] / (1024 * 1024), 2)
        self.stats['total_size_gb'] = round(self.stats['total_size_bytes'] / (1024 * 1024 * 1024), 3)
        return self.stats

    def scrape(self):
        """
        Main scraping method to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement scrape() method")

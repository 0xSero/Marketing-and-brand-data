"""
Marketing News Scraper
Scrapes marketing news and industry updates from various sources.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scrapers.base_scraper import BaseScraper
from utils.text_processor import TextProcessor
from utils.storage import DataStorage
from typing import List, Dict, Optional
from urllib.parse import urljoin
import time
import logging


class MarketingNewsScraper(BaseScraper):
    """
    Scraper for marketing news and updates.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        config: Dict,
        max_pages: int = 50,
        max_articles: int = 500
    ):
        super().__init__(name, base_url)

        self.config = config
        self.max_pages = max_pages
        self.max_articles = max_articles
        self.text_processor = TextProcessor()
        self.storage = DataStorage()

        # Selectors
        self.article_list_selector = config.get('article_list_selector', 'article')
        self.article_link_selector = config.get('article_link_selector', 'a')
        self.title_selector = config.get('title_selector', 'h1')
        self.content_selector = config.get('content_selector', 'article')
        self.author_selector = config.get('author_selector', '.author')
        self.date_selector = config.get('date_selector', 'time')
        self.category_selector = config.get('category_selector', '.category')
        self.pagination_selector = config.get('pagination_selector', '.next')
        self.archive_url_pattern = config.get('archive_url_pattern', '{base_url}/page/{page}')

    def get_archive_url(self, page: int) -> str:
        """Generate archive URL"""
        return self.archive_url_pattern.format(base_url=self.base_url, page=page)

    def scrape_article_urls(self) -> List[str]:
        """Scrape article URLs"""
        urls = []

        for page in range(1, self.max_pages + 1):
            if len(urls) >= self.max_articles:
                break

            archive_url = self.get_archive_url(page)
            self.logger.info(f"Scraping page {page}: {archive_url}")

            response = self.fetch_page(archive_url)
            if not response:
                break

            soup = self.parse_html(response.text)
            articles = soup.select(self.article_list_selector)

            if not articles:
                break

            for article in articles:
                link = article.select_one(self.article_link_selector)
                if link and link.get('href'):
                    url = urljoin(self.base_url, link['href'])
                    if url not in urls:
                        urls.append(url)

            self.logger.info(f"Found {len(articles)} articles, total: {len(urls)}")

        return urls[:self.max_articles]

    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape a single article"""
        if self.storage.content_exists(url):
            return None

        response = self.fetch_page(url)
        if not response:
            return None

        soup = self.parse_html(response.text)

        title = self.extract_text(soup, self.title_selector)
        author = self.extract_text(soup, self.author_selector)
        date = self.extract_text(soup, self.date_selector)
        category = self.extract_text(soup, self.category_selector)

        content_element = soup.select_one(self.content_selector)
        content = self.text_processor.extract_main_content(
            content_element if content_element else soup
        )

        metadata = self.extract_metadata(soup, url)
        metadata['category'] = category

        keywords = self.text_processor.extract_keywords(content)

        try:
            self.storage.save_content(
                url=url,
                title=title or metadata.get('title', ''),
                content=content,
                content_type='news',
                source=self.name,
                author=author,
                published_date=date,
                metadata=metadata,
                keywords=keywords
            )
            self.logger.info(f"Saved: {title[:50]}...")
        except Exception as e:
            self.logger.error(f"Failed to save {url}: {e}")
            return None

        self.mark_scraped(url)
        return {'url': url, 'title': title}

    def scrape(self):
        """Main scraping method"""
        self.logger.info(f"Starting scrape of {self.name}")
        start_time = time.time()

        urls = self.scrape_article_urls()
        successful = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            try:
                if self.scrape_article(url):
                    successful += 1
            except Exception as e:
                self.logger.error(f"Error: {e}")
                failed += 1

            if i % 10 == 0:
                stats = self.storage.get_statistics()
                self.logger.info(f"Progress: {i}/{len(urls)} | {stats['total_size_mb']} MB")

        duration = time.time() - start_time
        stats = self.get_stats()

        self.storage.save_scraping_run(
            scraper_name=self.name,
            total_items=len(urls),
            successful_items=successful,
            failed_items=failed,
            total_size_bytes=stats['total_size_bytes'],
            duration_seconds=duration
        )

        return stats


# News source configurations
NEWS_CONFIGS = {
    'adage': {
        'base_url': 'https://adage.com',
        'config': {
            'article_list_selector': 'article',
            'article_link_selector': 'h3 a, h2 a',
            'title_selector': 'h1',
            'content_selector': 'article, .article-body',
            'author_selector': '.author-name',
            'date_selector': 'time',
            'category_selector': '.category',
            'archive_url_pattern': 'https://adage.com/news/page/{page}',
        },
        'max_pages': 30,
        'max_articles': 300
    },
    'marketingweek': {
        'base_url': 'https://www.marketingweek.com',
        'config': {
            'article_list_selector': 'article',
            'article_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article',
            'author_selector': '.author',
            'date_selector': 'time',
            'category_selector': '.category',
            'archive_url_pattern': 'https://www.marketingweek.com/page/{page}/',
        },
        'max_pages': 30,
        'max_articles': 300
    },
    'thedrum': {
        'base_url': 'https://www.thedrum.com',
        'config': {
            'article_list_selector': 'article, .news-item',
            'article_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article',
            'author_selector': '.author',
            'date_selector': 'time',
            'category_selector': '.category',
            'archive_url_pattern': 'https://www.thedrum.com/news/page/{page}',
        },
        'max_pages': 30,
        'max_articles': 300
    },
    'adweek': {
        'base_url': 'https://www.adweek.com',
        'config': {
            'article_list_selector': 'article',
            'article_link_selector': 'h2 a, h3 a',
            'title_selector': 'h1',
            'content_selector': 'article',
            'author_selector': '.author-name',
            'date_selector': 'time',
            'category_selector': '.category',
            'archive_url_pattern': 'https://www.adweek.com/page/{page}/',
        },
        'max_pages': 30,
        'max_articles': 300
    },
    'campaignlive': {
        'base_url': 'https://www.campaignlive.com',
        'config': {
            'article_list_selector': 'article',
            'article_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article',
            'author_selector': '.author',
            'date_selector': 'time',
            'category_selector': '.section',
            'archive_url_pattern': 'https://www.campaignlive.com/news/page/{page}',
        },
        'max_pages': 30,
        'max_articles': 300
    }
}


class MarketingNewsScraperOrchestrator:
    """Orchestrates multiple news scrapers"""

    def __init__(self, sources: list = None):
        self.logger = logging.getLogger("MarketingNewsScraperOrchestrator")
        if sources:
            self.sources = {k: v for k, v in NEWS_CONFIGS.items() if k in sources}
        else:
            self.sources = NEWS_CONFIGS

    def scrape_all(self):
        """Scrape all news sources"""
        self.logger.info(f"Starting to scrape {len(self.sources)} news sources")

        total_stats = {'total_items': 0, 'total_size_mb': 0}

        for source_name, source_config in self.sources.items():
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Scraping: {source_name}")
            self.logger.info(f"{'='*60}\n")

            try:
                scraper = MarketingNewsScraper(
                    name=source_name,
                    base_url=source_config['base_url'],
                    config=source_config['config'],
                    max_pages=source_config.get('max_pages', 30),
                    max_articles=source_config.get('max_articles', 300)
                )

                stats = scraper.scrape()
                total_stats['total_items'] += stats.get('successful_scrapes', 0)
                total_stats['total_size_mb'] += stats.get('total_size_mb', 0)

            except Exception as e:
                self.logger.error(f"Error scraping {source_name}: {e}")

        self.logger.info(f"\nTotal articles: {total_stats['total_items']}")
        self.logger.info(f"Total size: {total_stats['total_size_mb']:.2f} MB")

        return total_stats

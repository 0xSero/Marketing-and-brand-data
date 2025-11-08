"""
Generic Blog Scraper
Flexible scraper for marketing blogs and publications.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scrapers.base_scraper import BaseScraper
from utils.text_processor import TextProcessor
from utils.storage import DataStorage
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin
import time


class GenericBlogScraper(BaseScraper):
    """
    Generic scraper for blog sites with configurable selectors.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        config: Dict[str, any],
        max_pages: int = 100,
        max_articles: int = 1000
    ):
        """
        Initialize generic blog scraper.

        Args:
            name: Scraper name
            base_url: Base URL of the blog
            config: Configuration dict with CSS selectors
            max_pages: Maximum pagination pages to scrape
            max_articles: Maximum articles to scrape
        """
        super().__init__(name, base_url)

        self.config = config
        self.max_pages = max_pages
        self.max_articles = max_articles
        self.text_processor = TextProcessor()
        self.storage = DataStorage()

        # Selectors from config
        self.article_list_selector = config.get('article_list_selector', 'article')
        self.article_link_selector = config.get('article_link_selector', 'a')
        self.title_selector = config.get('title_selector', 'h1')
        self.content_selector = config.get('content_selector', 'article')
        self.author_selector = config.get('author_selector', '.author')
        self.date_selector = config.get('date_selector', 'time')
        self.pagination_selector = config.get('pagination_selector', '.next')

        # Patterns
        self.archive_url_pattern = config.get('archive_url_pattern', '{base_url}/blog/page/{page}')
        self.article_url_pattern = config.get('article_url_pattern', None)

    def get_archive_url(self, page: int) -> str:
        """Generate archive URL for pagination"""
        return self.archive_url_pattern.format(base_url=self.base_url, page=page)

    def scrape_article_urls(self) -> List[str]:
        """
        Scrape article URLs from archive pages.

        Returns:
            List of article URLs
        """
        article_urls = []

        self.logger.info(f"Starting to scrape article URLs from {self.name}")

        for page in range(1, self.max_pages + 1):
            if len(article_urls) >= self.max_articles:
                break

            archive_url = self.get_archive_url(page)
            self.logger.info(f"Scraping archive page {page}: {archive_url}")

            response = self.fetch_page(archive_url)
            if not response:
                self.logger.warning(f"Failed to fetch archive page {page}")
                break

            soup = self.parse_html(response.text)

            # Find article links
            articles = soup.select(self.article_list_selector)

            if not articles:
                self.logger.info(f"No articles found on page {page}, stopping")
                break

            for article in articles:
                link = article.select_one(self.article_link_selector)
                if link and link.get('href'):
                    url = urljoin(self.base_url, link['href'])

                    # Apply URL pattern filter if configured
                    if self.article_url_pattern:
                        if not re.search(self.article_url_pattern, url):
                            continue

                    if url not in article_urls:
                        article_urls.append(url)

            self.logger.info(f"Found {len(articles)} articles on page {page}, total: {len(article_urls)}")

            # Check for next page
            next_page = soup.select_one(self.pagination_selector)
            if not next_page and page == 1:
                # Try to find pagination in different ways
                pagination = soup.find_all('a', href=re.compile(r'page|p=\d+'))
                if not pagination:
                    self.logger.info("No pagination found, this might be a single-page blog")
                    break

        self.logger.info(f"Total article URLs found: {len(article_urls)}")
        return article_urls[:self.max_articles]

    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article.

        Args:
            url: Article URL

        Returns:
            Article data dict or None
        """
        # Check if already in database
        if self.storage.content_exists(url):
            self.logger.info(f"Article already in database: {url}")
            return None

        response = self.fetch_page(url)
        if not response:
            return None

        soup = self.parse_html(response.text)

        # Extract data
        title = self.extract_text(soup, self.title_selector)
        author = self.extract_text(soup, self.author_selector)
        date = self.extract_text(soup, self.date_selector)

        # Extract main content
        content_element = soup.select_one(self.content_selector)
        if content_element:
            content = self.text_processor.extract_main_content(content_element)
        else:
            content = self.text_processor.extract_main_content(soup)

        # Extract metadata
        metadata = self.extract_metadata(soup, url)

        # Extract keywords
        keywords = self.text_processor.extract_keywords(content)

        article_data = {
            'url': url,
            'title': title or metadata.get('title', ''),
            'author': author or metadata.get('author', ''),
            'published_date': date or metadata.get('published_date', ''),
            'content': content,
            'metadata': metadata,
            'keywords': keywords,
            'word_count': len(content.split()),
            'source': self.name
        }

        # Save to storage
        try:
            self.storage.save_content(
                url=url,
                title=article_data['title'],
                content=content,
                content_type='article',
                source=self.name,
                author=article_data['author'],
                published_date=article_data['published_date'],
                metadata=metadata,
                keywords=keywords
            )
            self.logger.info(f"Saved article: {title[:50]}...")
        except Exception as e:
            self.logger.error(f"Failed to save article {url}: {e}")
            return None

        # Mark as scraped
        self.mark_scraped(url)

        return article_data

    def scrape(self):
        """Main scraping method"""
        self.logger.info(f"Starting scrape of {self.name}")
        start_time = time.time()

        # Get article URLs
        article_urls = self.scrape_article_urls()

        self.logger.info(f"Scraping {len(article_urls)} articles...")

        successful = 0
        failed = 0

        for i, url in enumerate(article_urls, 1):
            self.logger.info(f"Scraping article {i}/{len(article_urls)}: {url}")

            try:
                article = self.scrape_article(url)
                if article:
                    successful += 1
                else:
                    # Already existed or failed
                    pass
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                failed += 1

            # Progress update every 10 articles
            if i % 10 == 0:
                stats = self.storage.get_statistics()
                self.logger.info(
                    f"Progress: {i}/{len(article_urls)} | "
                    f"Success: {successful} | Failed: {failed} | "
                    f"Total DB size: {stats['total_size_mb']} MB"
                )

        duration = time.time() - start_time

        # Save run statistics
        stats = self.get_stats()
        self.storage.save_scraping_run(
            scraper_name=self.name,
            total_items=len(article_urls),
            successful_items=successful,
            failed_items=failed,
            total_size_bytes=stats['total_size_bytes'],
            duration_seconds=duration
        )

        self.logger.info(f"Scraping complete for {self.name}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info(f"Successful: {successful}, Failed: {failed}")
        self.logger.info(f"Data collected: {stats['total_size_mb']} MB")

        return stats

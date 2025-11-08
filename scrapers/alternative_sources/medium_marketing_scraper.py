"""
Medium Marketing Content Scraper
Scrapes publicly available marketing articles from Medium.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scrapers.base_scraper import BaseScraper
from utils.text_processor import TextProcessor
from utils.storage import DataStorage
import json
import time
import re
from typing import List, Dict
from urllib.parse import urljoin


class MediumMarketingScraper(BaseScraper):
    """
    Scrapes marketing content from Medium publications and tags.
    """

    def __init__(self, max_articles: int = 1000):
        super().__init__(
            name="medium_marketing",
            base_url="https://medium.com",
            rate_limit=2.0,
            respect_robots_txt=False  # For research purposes
        )
        self.max_articles = max_articles
        self.text_processor = TextProcessor()
        self.storage = DataStorage()

        # Marketing-focused Medium tags and publications
        self.marketing_tags = [
            'marketing', 'digital-marketing', 'content-marketing',
            'social-media-marketing', 'email-marketing', 'seo',
            'brand-strategy', 'branding', 'advertising',
            'growth-hacking', 'marketing-strategy', 'b2b-marketing',
            'startup-marketing', 'product-marketing', 'influencer-marketing'
        ]

        self.publications = [
            'marketing-and-entrepreneurship',
            'the-marketing-sage',
            'the-mission',
            'better-marketing'
        ]

    def scrape_tag(self, tag: str, max_articles: int = 100) -> List[str]:
        """Scrape article URLs from a Medium tag"""
        urls = []
        tag_url = f"{self.base_url}/tag/{tag}"

        self.logger.info(f"Scraping tag: {tag}")

        response = self.fetch_page(tag_url)
        if not response:
            return urls

        soup = self.parse_html(response.text)

        # Medium uses dynamic loading, so we'll get what's in the initial HTML
        article_links = soup.find_all('a', href=re.compile(r'^/@[\w-]+/[\w-]+'))

        for link in article_links[:max_articles]:
            href = link.get('href', '')
            if href:
                full_url = urljoin(self.base_url, href)
                # Clean URL (remove query parameters)
                full_url = full_url.split('?')[0]
                if full_url not in urls:
                    urls.append(full_url)

        self.logger.info(f"Found {len(urls)} articles for tag: {tag}")
        return urls

    def scrape_article(self, url: str) -> Dict:
        """Scrape a Medium article"""
        if self.storage.content_exists(url):
            self.logger.info(f"Article already exists: {url}")
            return None

        response = self.fetch_page(url)
        if not response:
            return None

        soup = self.parse_html(response.text)

        # Extract article content
        article = soup.find('article')
        if not article:
            return None

        # Extract title
        title_tag = article.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Extract author
        author = ""
        author_link = soup.find('a', {'data-action': 'show-user-card'})
        if not author_link:
            author_link = soup.find('a', href=re.compile(r'^/@[\w-]+$'))
        if author_link:
            author = author_link.get_text(strip=True)

        # Extract publication date
        date = ""
        time_tag = soup.find('time')
        if time_tag:
            date = time_tag.get('datetime', '') or time_tag.get_text(strip=True)

        # Extract main content
        content = self.text_processor.extract_main_content(article)

        if not content or len(content) < 100:
            return None

        # Extract tags
        tags = []
        tag_links = soup.find_all('a', href=re.compile(r'/tag/'))
        for tag_link in tag_links[:10]:
            tag = tag_link.get_text(strip=True)
            if tag:
                tags.append(tag)

        # Build article data
        article_data = {
            'url': url,
            'title': title,
            'author': author,
            'published_date': date,
            'content': content,
            'tags': tags,
            'source': 'medium',
            'content_type': 'article',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'word_count': len(content.split()),
            'platform': 'Medium'
        }

        # Save as JSONL
        self.save_as_jsonl(article_data)

        # Save to database
        self.storage.save_content(
            url=url,
            title=title,
            content=content,
            content_type='article',
            source='medium_marketing',
            author=author,
            published_date=date,
            metadata=article_data,
            keywords=tags
        )

        self.mark_scraped(url)
        return article_data

    def save_as_jsonl(self, article: Dict, output_file: str = "data/medium_marketing.jsonl"):
        """Save article as JSONL"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(article, ensure_ascii=False) + '\n')

    def scrape(self):
        """Main scraping method"""
        self.logger.info("Starting Medium marketing content scrape")

        start_time = time.time()
        all_urls = []

        # Collect URLs from tags
        for tag in self.marketing_tags:
            if len(all_urls) >= self.max_articles:
                break

            try:
                urls = self.scrape_tag(tag, max_articles=50)
                all_urls.extend(urls)
            except Exception as e:
                self.logger.error(f"Error scraping tag {tag}: {e}")

        # Remove duplicates
        all_urls = list(set(all_urls))[:self.max_articles]

        self.logger.info(f"Total unique articles to scrape: {len(all_urls)}")

        # Scrape articles
        successful = 0
        failed = 0

        for i, url in enumerate(all_urls, 1):
            self.logger.info(f"Scraping article {i}/{len(all_urls)}: {url}")

            try:
                article = self.scrape_article(url)
                if article:
                    successful += 1
                    self.logger.info(f"Saved: {article['title'][:50]}... ({article['word_count']} words)")
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                failed += 1

            # Progress update
            if i % 25 == 0:
                stats = self.storage.get_statistics()
                self.logger.info(f"Progress: {i}/{len(all_urls)} | {stats['total_size_mb']:.2f} MB")

        duration = time.time() - start_time

        self.logger.info(f"\nMedium scraping complete!")
        self.logger.info(f"Articles collected: {successful}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Duration: {duration:.2f} seconds")

        stats = self.storage.get_statistics()
        return {
            'successful': successful,
            'failed': failed,
            'duration': duration
        }


if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    scraper = MediumMarketingScraper(max_articles=500)
    scraper.scrape()

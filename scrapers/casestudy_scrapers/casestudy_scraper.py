"""
Case Study Scraper
Scrapes marketing case studies from various sources.
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
import logging


class CaseStudyScraper(BaseScraper):
    """
    Scraper for marketing case studies.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        config: Dict,
        max_pages: int = 50,
        max_items: int = 500
    ):
        """
        Initialize case study scraper.

        Args:
            name: Scraper name
            base_url: Base URL
            config: Configuration with selectors
            max_pages: Maximum pages to scrape
            max_items: Maximum items to scrape
        """
        super().__init__(name, base_url)

        self.config = config
        self.max_pages = max_pages
        self.max_items = max_items
        self.text_processor = TextProcessor()
        self.storage = DataStorage()

        # Selectors
        self.item_list_selector = config.get('item_list_selector', 'article')
        self.item_link_selector = config.get('item_link_selector', 'a')
        self.title_selector = config.get('title_selector', 'h1')
        self.content_selector = config.get('content_selector', 'article')
        self.company_selector = config.get('company_selector', '.company')
        self.industry_selector = config.get('industry_selector', '.industry')
        self.results_selector = config.get('results_selector', '.results')
        self.pagination_selector = config.get('pagination_selector', '.next')
        self.archive_url_pattern = config.get('archive_url_pattern', '{base_url}/page/{page}')

    def get_archive_url(self, page: int) -> str:
        """Generate archive URL"""
        return self.archive_url_pattern.format(base_url=self.base_url, page=page)

    def scrape_case_study_urls(self) -> List[str]:
        """Scrape case study URLs"""
        urls = []

        for page in range(1, self.max_pages + 1):
            if len(urls) >= self.max_items:
                break

            archive_url = self.get_archive_url(page)
            self.logger.info(f"Scraping page {page}: {archive_url}")

            response = self.fetch_page(archive_url)
            if not response:
                break

            soup = self.parse_html(response.text)
            items = soup.select(self.item_list_selector)

            if not items:
                self.logger.info(f"No items on page {page}")
                break

            for item in items:
                link = item.select_one(self.item_link_selector)
                if link and link.get('href'):
                    url = urljoin(self.base_url, link['href'])
                    if url not in urls:
                        urls.append(url)

            self.logger.info(f"Found {len(items)} items on page {page}, total: {len(urls)}")

        return urls[:self.max_items]

    def scrape_case_study(self, url: str) -> Optional[Dict]:
        """Scrape a single case study"""
        if self.storage.content_exists(url):
            self.logger.info(f"Case study already in database: {url}")
            return None

        response = self.fetch_page(url)
        if not response:
            return None

        soup = self.parse_html(response.text)

        # Extract data
        title = self.extract_text(soup, self.title_selector)
        company = self.extract_text(soup, self.company_selector)
        industry = self.extract_text(soup, self.industry_selector)
        results = self.extract_text(soup, self.results_selector)

        # Extract main content
        content_element = soup.select_one(self.content_selector)
        if content_element:
            content = self.text_processor.extract_main_content(content_element)
        else:
            content = self.text_processor.extract_main_content(soup)

        metadata = self.extract_metadata(soup, url)
        metadata['company'] = company
        metadata['industry'] = industry
        metadata['results'] = results

        keywords = self.text_processor.extract_keywords(content)

        # Save to storage
        try:
            self.storage.save_content(
                url=url,
                title=title or metadata.get('title', ''),
                content=content,
                content_type='case_study',
                source=self.name,
                metadata=metadata,
                keywords=keywords
            )
            self.logger.info(f"Saved case study: {title[:50]}...")
        except Exception as e:
            self.logger.error(f"Failed to save case study {url}: {e}")
            return None

        self.mark_scraped(url)

        return {
            'url': url,
            'title': title,
            'company': company,
            'industry': industry,
            'content': content
        }

    def scrape(self):
        """Main scraping method"""
        self.logger.info(f"Starting scrape of {self.name}")
        start_time = time.time()

        urls = self.scrape_case_study_urls()
        self.logger.info(f"Scraping {len(urls)} case studies...")

        successful = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            self.logger.info(f"Scraping {i}/{len(urls)}: {url}")

            try:
                item = self.scrape_case_study(url)
                if item:
                    successful += 1
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                failed += 1

            if i % 10 == 0:
                stats = self.storage.get_statistics()
                self.logger.info(
                    f"Progress: {i}/{len(urls)} | Success: {successful} | "
                    f"Failed: {failed} | Total: {stats['total_size_mb']} MB"
                )

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

        self.logger.info(f"Scraping complete: {successful} successful, {failed} failed")
        return stats


# Case study source configurations
CASESTUDY_CONFIGS = {
    'thinkwithgoogle': {
        'base_url': 'https://www.thinkwithgoogle.com',
        'config': {
            'item_list_selector': 'article, .case-study-card',
            'item_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article, .content',
            'company_selector': '.company-name',
            'industry_selector': '.industry',
            'results_selector': '.results, .outcome',
            'pagination_selector': '.next',
            'archive_url_pattern': 'https://www.thinkwithgoogle.com/case-studies/?page={page}',
        },
        'max_pages': 30,
        'max_items': 300
    },
    'hubspot_casestudies': {
        'base_url': 'https://www.hubspot.com',
        'config': {
            'item_list_selector': '.case-study-item, article',
            'item_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article, .case-study-content',
            'company_selector': '.customer-name',
            'industry_selector': '.industry',
            'results_selector': '.results',
            'pagination_selector': '.next',
            'archive_url_pattern': 'https://www.hubspot.com/case-studies?page={page}',
        },
        'max_pages': 20,
        'max_items': 200
    },
    'marketo_casestudies': {
        'base_url': 'https://www.marketo.com',
        'config': {
            'item_list_selector': '.resource-item, article',
            'item_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article',
            'company_selector': '.company',
            'industry_selector': '.industry',
            'results_selector': '.results',
            'pagination_selector': '.next',
            'archive_url_pattern': 'https://www.marketo.com/case-studies/page/{page}/',
        },
        'max_pages': 20,
        'max_items': 200
    }
}


class CaseStudyScraperOrchestrator:
    """Orchestrates multiple case study scrapers"""

    def __init__(self, sources: list = None):
        self.logger = logging.getLogger("CaseStudyScraperOrchestrator")
        if sources:
            self.sources = {k: v for k, v in CASESTUDY_CONFIGS.items() if k in sources}
        else:
            self.sources = CASESTUDY_CONFIGS

    def scrape_all(self):
        """Scrape all sources"""
        self.logger.info(f"Starting to scrape {len(self.sources)} case study sources")

        total_stats = {
            'total_items': 0,
            'total_size_mb': 0
        }

        for source_name, source_config in self.sources.items():
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Scraping: {source_name}")
            self.logger.info(f"{'='*60}\n")

            try:
                scraper = CaseStudyScraper(
                    name=source_name,
                    base_url=source_config['base_url'],
                    config=source_config['config'],
                    max_pages=source_config.get('max_pages', 30),
                    max_items=source_config.get('max_items', 300)
                )

                stats = scraper.scrape()
                total_stats['total_items'] += stats.get('successful_scrapes', 0)
                total_stats['total_size_mb'] += stats.get('total_size_mb', 0)

            except Exception as e:
                self.logger.error(f"Error scraping {source_name}: {e}")

        self.logger.info(f"\nTotal case studies: {total_stats['total_items']}")
        self.logger.info(f"Total size: {total_stats['total_size_mb']:.2f} MB")

        return total_stats

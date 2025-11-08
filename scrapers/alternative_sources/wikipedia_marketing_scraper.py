"""
Wikipedia Marketing Content Scraper
Scrapes marketing-related articles from Wikipedia (Creative Commons licensed).
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scrapers.base_scraper import BaseScraper
from utils.text_processor import TextProcessor
from utils.storage import DataStorage
import json
import time
from typing import List, Dict


class WikipediaMarketingScraper(BaseScraper):
    """
    Scrapes marketing-related content from Wikipedia.
    Wikipedia content is Creative Commons licensed and allows reuse.
    """

    def __init__(self, max_articles: int = 1000):
        super().__init__(
            name="wikipedia_marketing",
            base_url="https://en.wikipedia.org",
            rate_limit=1.0,  # Be respectful to Wikipedia
            respect_robots_txt=False  # For research purposes
        )
        self.max_articles = max_articles
        self.text_processor = TextProcessor()
        self.storage = DataStorage()

        # Marketing-related Wikipedia categories and articles
        self.marketing_topics = [
            # Core marketing concepts
            "Marketing", "Digital_marketing", "Content_marketing",
            "Social_media_marketing", "Email_marketing", "Influencer_marketing",
            "Affiliate_marketing", "Marketing_strategy", "Brand_management",
            "Advertising", "Public_relations", "Marketing_mix",

            # Brand and branding
            "Brand", "Branding", "Brand_equity", "Brand_awareness",
            "Brand_loyalty", "Rebranding", "Personal_branding",

            # Digital marketing
            "Search_engine_optimization", "Search_engine_marketing",
            "Pay-per-click", "Display_advertising", "Native_advertising",
            "Programmatic_advertising", "Marketing_automation",

            # Content and social
            "Content_strategy", "Viral_marketing", "Guerrilla_marketing",
            "Word-of-mouth_marketing", "Community_management",

            # Analytics and metrics
            "Marketing_analytics", "Conversion_rate_optimization",
            "Customer_relationship_management", "Customer_lifetime_value",
            "Marketing_attribution",

            # Campaigns and examples
            "Advertising_campaign", "Marketing_campaign",
            "Integrated_marketing_communications",

            # Market research
            "Market_research", "Market_segmentation", "Target_market",
            "Buyer_persona", "Customer_journey",

            # Channels
            "Direct_marketing", "Online_advertising", "Mobile_marketing",
            "Video_marketing", "Podcast_advertising",

            # Strategy
            "Growth_hacking", "Product_marketing", "B2B_marketing",
            "B2C_marketing", "Relationship_marketing",
            "Permission_marketing", "Inbound_marketing",
        ]

    def get_wikipedia_article(self, title: str) -> Dict:
        """Fetch a Wikipedia article via API"""
        api_url = f"{self.base_url}/w/api.php"

        params = {
            'action': 'query',
            'format': 'json',
            'titles': title.replace('_', ' '),
            'prop': 'extracts|info|categories',
            'explaintext': True,
            'inprop': 'url',
            'cllimit': 50
        }

        response = self.fetch_page(f"{api_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")

        if not response:
            return None

        try:
            data = response.json()
            pages = data.get('query', {}).get('pages', {})

            for page_id, page in pages.items():
                if page_id == '-1':  # Page doesn't exist
                    continue

                return {
                    'title': page.get('title', ''),
                    'content': page.get('extract', ''),
                    'url': page.get('fullurl', ''),
                    'categories': [cat.get('title', '').replace('Category:', '')
                                 for cat in page.get('categories', [])],
                    'page_id': page_id
                }
        except Exception as e:
            self.logger.error(f"Error parsing Wikipedia response for {title}: {e}")

        return None

    def get_related_articles(self, title: str, limit: int = 20) -> List[str]:
        """Get related articles from a Wikipedia page"""
        api_url = f"{self.base_url}/w/api.php"

        params = {
            'action': 'query',
            'format': 'json',
            'titles': title.replace('_', ' '),
            'prop': 'links',
            'pllimit': limit
        }

        response = self.fetch_page(f"{api_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")

        if not response:
            return []

        try:
            data = response.json()
            pages = data.get('query', {}).get('pages', {})

            for page_id, page in pages.items():
                links = page.get('links', [])
                return [link['title'] for link in links if 'title' in link]
        except Exception as e:
            self.logger.error(f"Error getting related articles for {title}: {e}")

        return []

    def save_as_jsonl(self, article: Dict, output_file: str = "data/wikipedia_marketing.jsonl"):
        """Save article as JSONL"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(article, ensure_ascii=False) + '\n')

    def scrape(self):
        """Main scraping method"""
        self.logger.info(f"Starting Wikipedia marketing content scrape")
        self.logger.info(f"Target: {self.max_articles} articles")

        start_time = time.time()
        scraped_articles = []
        processed_titles = set()
        to_process = list(self.marketing_topics)

        successful = 0
        failed = 0

        while to_process and len(scraped_articles) < self.max_articles:
            title = to_process.pop(0)

            if title in processed_titles:
                continue

            processed_titles.add(title)

            self.logger.info(f"Scraping: {title} ({len(scraped_articles)}/{self.max_articles})")

            try:
                article = self.get_wikipedia_article(title)

                if article and article.get('content'):
                    # Add metadata
                    article['source'] = 'wikipedia'
                    article['content_type'] = 'encyclopedia_article'
                    article['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    article['word_count'] = len(article['content'].split())
                    article['license'] = 'Creative Commons Attribution-ShareAlike 3.0'

                    # Save as JSONL
                    self.save_as_jsonl(article)

                    # Also save to database
                    self.storage.save_content(
                        url=article['url'],
                        title=article['title'],
                        content=article['content'],
                        content_type='encyclopedia_article',
                        source='wikipedia_marketing',
                        metadata=article,
                        keywords=article.get('categories', [])
                    )

                    scraped_articles.append(article)
                    successful += 1

                    self.logger.info(f"Saved: {article['title']} ({article['word_count']} words)")

                    # Get related articles to expand coverage
                    if len(scraped_articles) < self.max_articles:
                        related = self.get_related_articles(title, limit=10)
                        for related_title in related:
                            if related_title not in processed_titles and related_title not in to_process:
                                # Filter for marketing-related content
                                if any(keyword in related_title.lower() for keyword in [
                                    'market', 'brand', 'advertis', 'campaign', 'promotion',
                                    'customer', 'consumer', 'product', 'sales', 'strategy'
                                ]):
                                    to_process.append(related_title)
                else:
                    failed += 1

            except Exception as e:
                self.logger.error(f"Error scraping {title}: {e}")
                failed += 1

            # Progress update
            if len(scraped_articles) % 50 == 0 and len(scraped_articles) > 0:
                stats = self.storage.get_statistics()
                self.logger.info(f"Progress: {len(scraped_articles)} articles | {stats['total_size_mb']:.2f} MB")

        duration = time.time() - start_time

        self.logger.info(f"\nWikipedia scraping complete!")
        self.logger.info(f"Articles collected: {successful}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Duration: {duration:.2f} seconds")

        stats = self.storage.get_statistics()
        self.logger.info(f"Total data: {stats['total_size_mb']:.2f} MB ({stats['total_size_gb']:.3f} GB)")

        return {
            'successful': successful,
            'failed': failed,
            'duration': duration,
            'articles': scraped_articles
        }


if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    scraper = WikipediaMarketingScraper(max_articles=1000)
    scraper.scrape()

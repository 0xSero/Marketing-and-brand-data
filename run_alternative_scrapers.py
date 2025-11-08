#!/usr/bin/env python3
"""
Alternative Marketing Data Scrapers
Runs Wikipedia, Medium, and Reddit scrapers to collect marketing content.
These sources are more accessible and allow scraping with proper rate limiting.
"""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent))

from scrapers.alternative_sources.wikipedia_marketing_scraper import WikipediaMarketingScraper
from scrapers.alternative_sources.medium_marketing_scraper import MediumMarketingScraper
from scrapers.alternative_sources.reddit_marketing_scraper import RedditMarketingScraper
from utils.storage import DataStorage


def setup_logging():
    """Setup logging"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"alternative_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )

    return logging.getLogger("AlternativeScrapers")


def main():
    logger = setup_logging()

    logger.info("="*80)
    logger.info("ALTERNATIVE MARKETING KNOWLEDGE SCRAPERS")
    logger.info("="*80)
    logger.info("Sources: Wikipedia, Medium, Reddit")
    logger.info(f"Start time: {datetime.now()}")
    logger.info("="*80 + "\n")

    total_start_time = time.time()
    storage = DataStorage()

    # Track totals
    total_items = 0
    results = {}

    # 1. Wikipedia Scraper (Largest source - ~1000 articles)
    try:
        logger.info("\n" + "="*80)
        logger.info("SCRAPING WIKIPEDIA MARKETING CONTENT")
        logger.info("="*80 + "\n")

        wiki_scraper = WikipediaMarketingScraper(max_articles=1000)
        wiki_results = wiki_scraper.scrape()
        results['wikipedia'] = wiki_results
        total_items += wiki_results.get('successful', 0)

        logger.info(f"Wikipedia complete: {wiki_results.get('successful', 0)} articles")

    except Exception as e:
        logger.error(f"Wikipedia scraper error: {e}")
        import traceback
        traceback.print_exc()

    # 2. Medium Scraper (~500 articles)
    try:
        logger.info("\n" + "="*80)
        logger.info("SCRAPING MEDIUM MARKETING CONTENT")
        logger.info("="*80 + "\n")

        medium_scraper = MediumMarketingScraper(max_articles=500)
        medium_results = medium_scraper.scrape()
        results['medium'] = medium_results
        total_items += medium_results.get('successful', 0)

        logger.info(f"Medium complete: {medium_results.get('successful', 0)} articles")

    except Exception as e:
        logger.error(f"Medium scraper error: {e}")
        import traceback
        traceback.print_exc()

    # 3. Reddit Scraper (~500 posts)
    try:
        logger.info("\n" + "="*80)
        logger.info("SCRAPING REDDIT MARKETING DISCUSSIONS")
        logger.info("="*80 + "\n")

        reddit_scraper = RedditMarketingScraper(max_posts=500)
        reddit_results = reddit_scraper.scrape()
        results['reddit'] = reddit_results
        total_items += reddit_results.get('successful', 0)

        logger.info(f"Reddit complete: {reddit_results.get('successful', 0)} posts")

    except Exception as e:
        logger.error(f"Reddit scraper error: {e}")
        import traceback
        traceback.print_exc()

    # Final statistics
    total_duration = time.time() - total_start_time
    db_stats = storage.get_statistics()

    logger.info("\n" + "="*80)
    logger.info("ALL SCRAPING COMPLETE - FINAL SUMMARY")
    logger.info("="*80)
    logger.info(f"Total duration: {total_duration/3600:.2f} hours ({total_duration:.0f} seconds)")
    logger.info(f"Total items collected: {db_stats['total_items']}")
    logger.info(f"Total words: {db_stats.get('total_words', 0):,}")
    logger.info(f"Total size: {db_stats['total_size_mb']:.2f} MB ({db_stats['total_size_gb']:.3f} GB)")

    logger.info(f"\nBreakdown by source:")
    for source, count in db_stats.get('by_source', {}).items():
        logger.info(f"  {source:30} {count:>6} items")

    logger.info(f"\nBreakdown by type:")
    for content_type, count in db_stats.get('by_type', {}).items():
        logger.info(f"  {content_type:30} {count:>6} items")

    logger.info("\nJSONL files created:")
    logger.info("  - data/wikipedia_marketing.jsonl")
    logger.info("  - data/medium_marketing.jsonl")
    logger.info("  - data/reddit_marketing.jsonl")

    logger.info("="*80)

    # Check if we need more data to reach 2GB target
    if db_stats['total_size_gb'] < 2.0:
        remaining_gb = 2.0 - db_stats['total_size_gb']
        logger.info(f"\nNote: Current size {db_stats['total_size_gb']:.3f} GB")
        logger.info(f"To reach 2GB target, need {remaining_gb:.3f} GB more data")
        logger.info("Consider increasing max_articles/max_posts in scrapers, or adding more sources")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Real Marketing Content Scraper
Step 1: Scrape GitHub repos for marketing resource links
Step 2: Scrape actual content from those links using advanced techniques
"""

import sys
from pathlib import Path
import logging
import json
import time
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from scrapers.real_content.github_scraper import GitHubMarketingScraper
from scrapers.real_content.advanced_web_scraper import AdvancedWebScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("="*80)
    logger.info("REAL MARKETING CONTENT SCRAPER")
    logger.info("="*80)
    logger.info("Step 1: Scraping GitHub repositories for marketing links...")
    logger.info("="*80 + "\n")

    # Step 1: Scrape GitHub repos
    github_scraper = GitHubMarketingScraper()
    repos_data = github_scraper.scrape_all_repos()

    # Collect all links
    all_links = []
    for repo in repos_data:
        for link in repo.get('extracted_links', []):
            all_links.append(link['url'])

    # Deduplicate
    all_links = list(set(all_links))

    logger.info(f"\n{'='*80}")
    logger.info(f"Found {len(all_links)} unique marketing content links")
    logger.info(f"{'='*80}\n")

    # Step 2: Scrape actual content
    logger.info("Step 2: Scraping actual content from links...")
    logger.info("Using advanced techniques to bypass 403 errors...")
    logger.info("="*80 + "\n")

    web_scraper = AdvancedWebScraper(rate_limit=2)

    # Start scraping
    start_time = time.time()
    successful, failed = web_scraper.scrape_urls(
        all_links[:500],  # Start with first 500, can increase
        output_file='data/real_marketing_content.jsonl'
    )

    duration = time.time() - start_time

    logger.info(f"\n{'='*80}")
    logger.info(f"SCRAPING COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"Duration: {duration/60:.2f} minutes")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success rate: {successful/(successful+failed)*100:.1f}%")

    # Check file size
    output_file = Path('data/real_marketing_content.jsonl')
    if output_file.exists():
        size_mb = output_file.stat().st_size / (1024 * 1024)
        logger.info(f"File size: {size_mb:.2f} MB")

        # Count lines
        with open(output_file, 'r') as f:
            line_count = sum(1 for _ in f)
        logger.info(f"Articles collected: {line_count}")

    logger.info(f"{'='*80}")


if __name__ == '__main__':
    main()

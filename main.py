#!/usr/bin/env python3
"""
Marketing Knowledge Database Scraper
Main orchestrator for scraping marketing content from multiple sources.

Usage:
    python main.py --all                    # Scrape all sources
    python main.py --blogs                  # Scrape only blogs
    python main.py --case-studies          # Scrape only case studies
    python main.py --news                  # Scrape only news
    python main.py --stats                 # Show database statistics
    python main.py --export output.json    # Export database to JSON
"""

import argparse
import logging
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Import scrapers
from scrapers.blog_scrapers.marketing_blogs_scraper import MarketingBlogsScraper
from scrapers.casestudy_scrapers.casestudy_scraper import CaseStudyScraperOrchestrator
from scrapers.news_scrapers.marketing_news_scraper import MarketingNewsScraperOrchestrator
from utils.storage import DataStorage


# Setup logging
def setup_logging(log_file: str = None):
    """Configure logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        handlers.append(logging.FileHandler(log_dir / log_file))

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers
    )


class MarketingKnowledgeScraper:
    """
    Main orchestrator for all marketing knowledge scrapers.
    """

    def __init__(self, config_file: str = "config/sources.json"):
        """
        Initialize the scraper.

        Args:
            config_file: Path to configuration file
        """
        self.logger = logging.getLogger("MarketingKnowledgeScraper")

        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.storage = DataStorage()
        self.total_stats = {
            'start_time': datetime.now(),
            'blogs': {},
            'case_studies': {},
            'news': {},
            'total_items': 0,
            'total_size_gb': 0
        }

    def scrape_blogs(self):
        """Scrape all blog sources"""
        if not self.config['scrapers']['blogs']['enabled']:
            self.logger.info("Blog scraping is disabled in config")
            return

        self.logger.info("\n" + "="*80)
        self.logger.info("STARTING BLOG SCRAPING")
        self.logger.info("="*80 + "\n")

        sources = self.config['scrapers']['blogs'].get('sources', [])
        scraper = MarketingBlogsScraper(blogs=sources if sources else None)

        stats = scraper.scrape_all()
        self.total_stats['blogs'] = stats

        return stats

    def scrape_case_studies(self):
        """Scrape all case study sources"""
        if not self.config['scrapers']['case_studies']['enabled']:
            self.logger.info("Case study scraping is disabled in config")
            return

        self.logger.info("\n" + "="*80)
        self.logger.info("STARTING CASE STUDY SCRAPING")
        self.logger.info("="*80 + "\n")

        sources = self.config['scrapers']['case_studies'].get('sources', [])
        scraper = CaseStudyScraperOrchestrator(sources=sources if sources else None)

        stats = scraper.scrape_all()
        self.total_stats['case_studies'] = stats

        return stats

    def scrape_news(self):
        """Scrape all news sources"""
        if not self.config['scrapers']['news']['enabled']:
            self.logger.info("News scraping is disabled in config")
            return

        self.logger.info("\n" + "="*80)
        self.logger.info("STARTING NEWS SCRAPING")
        self.logger.info("="*80 + "\n")

        sources = self.config['scrapers']['news'].get('sources', [])
        scraper = MarketingNewsScraperOrchestrator(sources=sources if sources else None)

        stats = scraper.scrape_all()
        self.total_stats['news'] = stats

        return stats

    def scrape_all(self):
        """Scrape all sources"""
        self.logger.info("="*80)
        self.logger.info("MARKETING KNOWLEDGE DATABASE SCRAPER")
        self.logger.info("="*80)
        self.logger.info(f"Target size: {self.config['target_size_gb']} GB")
        self.logger.info(f"Start time: {self.total_stats['start_time']}")
        self.logger.info("="*80 + "\n")

        start_time = time.time()

        # Scrape all categories
        try:
            self.scrape_blogs()
        except Exception as e:
            self.logger.error(f"Error in blog scraping: {e}")
            import traceback
            traceback.print_exc()

        try:
            self.scrape_case_studies()
        except Exception as e:
            self.logger.error(f"Error in case study scraping: {e}")
            import traceback
            traceback.print_exc()

        try:
            self.scrape_news()
        except Exception as e:
            self.logger.error(f"Error in news scraping: {e}")
            import traceback
            traceback.print_exc()

        # Calculate totals
        duration = time.time() - start_time
        db_stats = self.storage.get_statistics()

        # Final summary
        self.logger.info("\n" + "="*80)
        self.logger.info("SCRAPING COMPLETE - FINAL SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Duration: {duration/3600:.2f} hours ({duration:.0f} seconds)")
        self.logger.info(f"Total items collected: {db_stats['total_items']}")
        self.logger.info(f"Total words: {db_stats.get('total_words', 0):,}")
        self.logger.info(f"Total size: {db_stats['total_size_mb']:.2f} MB ({db_stats['total_size_gb']:.3f} GB)")
        self.logger.info(f"\nBreakdown by source:")
        for source, count in db_stats.get('by_source', {}).items():
            self.logger.info(f"  - {source}: {count} items")
        self.logger.info(f"\nBreakdown by type:")
        for content_type, count in db_stats.get('by_type', {}).items():
            self.logger.info(f"  - {content_type}: {count} items")
        self.logger.info("="*80)

        # Save summary to file
        summary_file = Path('data/scraping_summary.json')
        with open(summary_file, 'w') as f:
            json.dump({
                'completion_time': datetime.now().isoformat(),
                'duration_seconds': duration,
                'duration_hours': duration / 3600,
                'database_stats': db_stats,
                'config': self.config
            }, f, indent=2)

        self.logger.info(f"\nSummary saved to: {summary_file}")

        return db_stats

    def show_stats(self):
        """Display database statistics"""
        stats = self.storage.get_statistics()

        print("\n" + "="*80)
        print("MARKETING KNOWLEDGE DATABASE STATISTICS")
        print("="*80)
        print(f"Total items: {stats['total_items']}")
        print(f"Total words: {stats.get('total_words', 0):,}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB ({stats['total_size_gb']:.3f} GB)")

        print(f"\nBy Source:")
        for source, count in sorted(stats.get('by_source', {}).items()):
            print(f"  {source:30} {count:>6} items")

        print(f"\nBy Content Type:")
        for content_type, count in sorted(stats.get('by_type', {}).items()):
            print(f"  {content_type:30} {count:>6} items")

        print("="*80 + "\n")

    def export_to_json(self, output_file: str):
        """Export database to JSON"""
        self.logger.info(f"Exporting database to {output_file}")
        self.storage.export_to_json(output_file)
        self.logger.info("Export complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Marketing Knowledge Database Scraper'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Scrape all sources (blogs, case studies, news)'
    )
    parser.add_argument(
        '--blogs',
        action='store_true',
        help='Scrape only marketing blogs'
    )
    parser.add_argument(
        '--case-studies',
        action='store_true',
        help='Scrape only case studies'
    )
    parser.add_argument(
        '--news',
        action='store_true',
        help='Scrape only marketing news'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    parser.add_argument(
        '--export',
        type=str,
        help='Export database to JSON file'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/sources.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file name (default: scraper_YYYYMMDD_HHMMSS.log)'
    )

    args = parser.parse_args()

    # Setup logging
    log_file = args.log_file or f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging(log_file)

    # Initialize scraper
    scraper = MarketingKnowledgeScraper(config_file=args.config)

    # Execute commands
    if args.stats:
        scraper.show_stats()
    elif args.export:
        scraper.export_to_json(args.export)
    elif args.all:
        scraper.scrape_all()
    elif args.blogs:
        scraper.scrape_blogs()
    elif args.case_studies:
        scraper.scrape_case_studies()
    elif args.news:
        scraper.scrape_news()
    else:
        # Default: scrape all
        print("No specific option selected. Use --help for options.")
        print("To start scraping, use: python main.py --all")
        parser.print_help()


if __name__ == '__main__':
    main()

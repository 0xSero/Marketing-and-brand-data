#!/usr/bin/env python3
"""
Full Marketing Data Scraper (Non-commercial Research Use)
Scrapes marketing blogs with robots.txt checking disabled for research purposes.
"""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from scrapers.blog_scrapers.marketing_blogs_scraper import MarketingBlogsScraper, BLOG_CONFIGS
from scrapers.blog_scrapers.generic_blog_scraper import GenericBlogScraper
from utils.storage import DataStorage
import json


# Setup logging
def setup_logging():
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"full_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )

    return logging.getLogger("FullScraper")


def save_jsonl(data, filename):
    """Save data as JSONL"""
    filepath = Path("data") / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')


def main():
    logger = setup_logging()

    logger.info("="*80)
    logger.info("FULL MARKETING KNOWLEDGE SCRAPER")
    logger.info("Mode: Research - robots.txt checking disabled")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now()}")
    logger.info("="*80 + "\n")

    total_start_time = time.time()
    storage = DataStorage()

    total_articles = 0
    total_size_mb = 0

    # Scrape each blog
    for blog_name, blog_config in BLOG_CONFIGS.items():
        logger.info(f"\n{'='*80}")
        logger.info(f"SCRAPING: {blog_name}")
        logger.info(f"{'='*80}\n")

        try:
            scraper = GenericBlogScraper(
                name=blog_name,
                base_url=blog_config['base_url'],
                config=blog_config['config'],
                max_pages=blog_config.get('max_pages', 50),
                max_articles=blog_config.get('max_articles', 500),
                respect_robots_txt=False  # Disabled for research
            )

            # Get article URLs
            article_urls = scraper.scrape_article_urls()
            logger.info(f"Found {len(article_urls)} article URLs")

            successful = 0
            failed = 0

            for i, url in enumerate(article_urls, 1):
                try:
                    response = scraper.fetch_page(url)
                    if not response:
                        failed += 1
                        continue

                    soup = scraper.parse_html(response.text)

                    # Extract article data
                    title = scraper.extract_text(soup, scraper.title_selector)
                    author = scraper.extract_text(soup, scraper.author_selector)
                    date = scraper.extract_text(soup, scraper.date_selector)

                    content_element = soup.select_one(scraper.content_selector)
                    if content_element:
                        content = scraper.text_processor.extract_main_content(content_element)
                    else:
                        content = scraper.text_processor.extract_main_content(soup)

                    if not content or len(content) < 100:
                        failed += 1
                        continue

                    metadata = scraper.extract_metadata(soup, url)
                    keywords = scraper.text_processor.extract_keywords(content)

                    article_data = {
                        'url': url,
                        'title': title or metadata.get('title', ''),
                        'author': author or metadata.get('author', ''),
                        'published_date': date or metadata.get('published_date', ''),
                        'content': content,
                        'source': blog_name,
                        'content_type': 'article',
                        'category': 'marketing_blog',
                        'tags': keywords[:10],
                        'word_count': len(content.split()),
                        'scraped_at': datetime.now().isoformat()
                    }

                    # Save as JSONL
                    save_jsonl(article_data, f"{blog_name}_articles.jsonl")

                    # Save to database
                    storage.save_content(
                        url=url,
                        title=article_data['title'],
                        content=content,
                        content_type='article',
                        source=blog_name,
                        author=article_data['author'],
                        published_date=article_data['published_date'],
                        metadata=metadata,
                        keywords=keywords
                    )

                    successful += 1
                    scraper.mark_scraped(url)

                    if successful % 10 == 0:
                        logger.info(f"Progress: {successful}/{len(article_urls)} articles scraped")

                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    failed += 1

            logger.info(f"Completed {blog_name}: {successful} successful, {failed} failed")
            total_articles += successful

        except Exception as e:
            logger.error(f"Error with {blog_name}: {e}")
            import traceback
            traceback.print_exc()

    # Final statistics
    duration = time.time() - total_start_time
    db_stats = storage.get_statistics()

    logger.info("\n" + "="*80)
    logger.info("SCRAPING COMPLETE")
    logger.info("="*80)
    logger.info(f"Duration: {duration/3600:.2f} hours")
    logger.info(f"Total articles: {db_stats['total_items']}")
    logger.info(f"Total size: {db_stats['total_size_mb']:.2f} MB ({db_stats['total_size_gb']:.3f} GB)")
    logger.info("\nJSONL files in data/")
    logger.info("="*80)


if __name__ == '__main__':
    main()

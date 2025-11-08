"""
Marketing Blogs Scraper
Scrapes multiple popular marketing blogs.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scrapers.blog_scrapers.generic_blog_scraper import GenericBlogScraper
import logging


# Blog configurations
BLOG_CONFIGS = {
    'hubspot': {
        'base_url': 'https://blog.hubspot.com',
        'config': {
            'article_list_selector': 'article.blog-post-card, div.blog-post-card',
            'article_link_selector': 'a.blog-post-card__link, h3 a',
            'title_selector': 'h1, .blog-post__title',
            'content_selector': 'article, .blog-post__content, .post-body',
            'author_selector': '.blog-author__name, .author-name',
            'date_selector': 'time, .blog-post__date',
            'pagination_selector': '.pagination__next, a[rel="next"]',
            'archive_url_pattern': 'https://blog.hubspot.com/marketing?page={page}',
        },
        'max_pages': 50,
        'max_articles': 500
    },
    'neilpatel': {
        'base_url': 'https://neilpatel.com',
        'config': {
            'article_list_selector': 'article, .post-item',
            'article_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article, .post-content',
            'author_selector': '.author-name',
            'date_selector': 'time, .publish-date',
            'pagination_selector': '.next-page',
            'archive_url_pattern': 'https://neilpatel.com/blog/page/{page}/',
        },
        'max_pages': 50,
        'max_articles': 500
    },
    'moz': {
        'base_url': 'https://moz.com',
        'config': {
            'article_list_selector': 'article, .post-listing',
            'article_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article, .entry-content',
            'author_selector': '.author',
            'date_selector': 'time',
            'pagination_selector': '.next',
            'archive_url_pattern': 'https://moz.com/blog/page/{page}',
        },
        'max_pages': 40,
        'max_articles': 400
    },
    'contentmarketinginstitute': {
        'base_url': 'https://contentmarketinginstitute.com',
        'config': {
            'article_list_selector': 'article',
            'article_link_selector': 'h2 a, h3 a',
            'title_selector': 'h1',
            'content_selector': 'article, .entry-content',
            'author_selector': '.author-name',
            'date_selector': 'time',
            'pagination_selector': '.next',
            'archive_url_pattern': 'https://contentmarketinginstitute.com/articles/page/{page}/',
        },
        'max_pages': 40,
        'max_articles': 400
    },
    'marketingprofs': {
        'base_url': 'https://www.marketingprofs.com',
        'config': {
            'article_list_selector': 'article, .article-item',
            'article_link_selector': 'a',
            'title_selector': 'h1',
            'content_selector': 'article, .article-content',
            'author_selector': '.author',
            'date_selector': 'time',
            'pagination_selector': '.next',
            'archive_url_pattern': 'https://www.marketingprofs.com/articles/page/{page}',
        },
        'max_pages': 30,
        'max_articles': 300
    },
    'copyblogger': {
        'base_url': 'https://copyblogger.com',
        'config': {
            'article_list_selector': 'article',
            'article_link_selector': 'h2 a',
            'title_selector': 'h1',
            'content_selector': 'article, .entry-content',
            'author_selector': '.author-name',
            'date_selector': 'time',
            'pagination_selector': '.next',
            'archive_url_pattern': 'https://copyblogger.com/blog/page/{page}/',
        },
        'max_pages': 30,
        'max_articles': 300
    },
    'searchengineland': {
        'base_url': 'https://searchengineland.com',
        'config': {
            'article_list_selector': 'article',
            'article_link_selector': 'h3 a',
            'title_selector': 'h1',
            'content_selector': 'article',
            'author_selector': '.author-name',
            'date_selector': 'time',
            'pagination_selector': '.next',
            'archive_url_pattern': 'https://searchengineland.com/page/{page}',
        },
        'max_pages': 40,
        'max_articles': 400
    }
}


class MarketingBlogsScraper:
    """
    Orchestrates scraping of multiple marketing blogs.
    """

    def __init__(self, blogs: list = None):
        """
        Initialize scraper.

        Args:
            blogs: List of blog names to scrape (default: all)
        """
        self.logger = logging.getLogger("MarketingBlogsScraper")

        if blogs:
            self.blogs = {k: v for k, v in BLOG_CONFIGS.items() if k in blogs}
        else:
            self.blogs = BLOG_CONFIGS

    def scrape_all(self):
        """Scrape all configured blogs"""
        self.logger.info(f"Starting to scrape {len(self.blogs)} marketing blogs")

        total_stats = {
            'total_articles': 0,
            'total_size_mb': 0,
            'total_size_gb': 0
        }

        for blog_name, blog_config in self.blogs.items():
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Starting scrape of: {blog_name}")
            self.logger.info(f"{'='*60}\n")

            try:
                scraper = GenericBlogScraper(
                    name=blog_name,
                    base_url=blog_config['base_url'],
                    config=blog_config['config'],
                    max_pages=blog_config.get('max_pages', 50),
                    max_articles=blog_config.get('max_articles', 500)
                )

                stats = scraper.scrape()

                total_stats['total_articles'] += stats.get('successful_scrapes', 0)
                total_stats['total_size_mb'] += stats.get('total_size_mb', 0)
                total_stats['total_size_gb'] += stats.get('total_size_gb', 0)

                self.logger.info(f"Completed scrape of {blog_name}")
                self.logger.info(f"Articles: {stats.get('successful_scrapes', 0)}")
                self.logger.info(f"Size: {stats.get('total_size_mb', 0)} MB")

            except Exception as e:
                self.logger.error(f"Error scraping {blog_name}: {e}")
                import traceback
                traceback.print_exc()

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"ALL BLOGS SCRAPING COMPLETE")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total articles: {total_stats['total_articles']}")
        self.logger.info(f"Total size: {total_stats['total_size_mb']:.2f} MB ({total_stats['total_size_gb']:.3f} GB)")

        return total_stats

    def scrape_blog(self, blog_name: str):
        """Scrape a specific blog"""
        if blog_name not in BLOG_CONFIGS:
            raise ValueError(f"Unknown blog: {blog_name}")

        blog_config = BLOG_CONFIGS[blog_name]

        scraper = GenericBlogScraper(
            name=blog_name,
            base_url=blog_config['base_url'],
            config=blog_config['config'],
            max_pages=blog_config.get('max_pages', 50),
            max_articles=blog_config.get('max_articles', 500)
        )

        return scraper.scrape()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    scraper = MarketingBlogsScraper()
    scraper.scrape_all()

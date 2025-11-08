"""
Reddit Marketing Content Scraper
Scrapes publicly available marketing discussions and content from Reddit.
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


class RedditMarketingScraper(BaseScraper):
    """
    Scrapes marketing content from relevant subreddits.
    Uses old.reddit.com for easier HTML parsing.
    """

    def __init__(self, max_posts: int = 1000):
        super().__init__(
            name="reddit_marketing",
            base_url="https://old.reddit.com",
            rate_limit=2.0,
            respect_robots_txt=False  # For research purposes
        )
        self.max_posts = max_posts
        self.text_processor = TextProcessor()
        self.storage = DataStorage()

        # Marketing-related subreddits
        self.subreddits = [
            'marketing', 'digital_marketing', 'socialmedia',
            'SEO', 'PPC', 'content_marketing', 'emailmarketing',
            'advertising', 'socialmediamarketing', 'GrowthHacking',
            'marketing_analytics', 'Entrepreneur', 'startups',
            'Branding', 'copywriting', 'AskMarketing'
        ]

    def scrape_subreddit(self, subreddit: str, sort: str = 'top', time_filter: str = 'all', limit: int = 100) -> List[str]:
        """Scrape post URLs from a subreddit"""
        urls = []

        # Build URL
        if sort == 'top':
            url = f"{self.base_url}/r/{subreddit}/top/?t={time_filter}"
        elif sort == 'hot':
            url = f"{self.base_url}/r/{subreddit}/hot/"
        else:
            url = f"{self.base_url}/r/{subreddit}/"

        self.logger.info(f"Scraping r/{subreddit} ({sort}/{time_filter})")

        response = self.fetch_page(url)
        if not response:
            return urls

        soup = self.parse_html(response.text)

        # Find post links
        posts = soup.find_all('div', class_='thing', limit=limit)

        for post in posts:
            data_permalink = post.get('data-permalink')
            if data_permalink:
                full_url = urljoin(self.base_url, data_permalink)
                urls.append(full_url)

        self.logger.info(f"Found {len(urls)} posts from r/{subreddit}")
        return urls

    def scrape_post(self, url: str) -> Dict:
        """Scrape a Reddit post"""
        if self.storage.content_exists(url):
            self.logger.info(f"Post already exists: {url}")
            return None

        response = self.fetch_page(url)
        if not response:
            return None

        soup = self.parse_html(response.text)

        # Extract post data
        thing = soup.find('div', class_='thing')
        if not thing:
            return None

        # Title
        title_tag = thing.find('a', class_='title')
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Author
        author_tag = thing.find('a', class_='author')
        author = author_tag.get_text(strip=True) if author_tag else "[deleted]"

        # Subreddit
        subreddit_tag = thing.find('a', class_='subreddit')
        subreddit = subreddit_tag.get_text(strip=True) if subreddit_tag else ""

        # Score
        score_tag = thing.find('div', class_='score')
        if not score_tag:
            score_tag = thing.find('div', class_='score unvoted')
        score = score_tag.get_text(strip=True) if score_tag else "0"

        # Post content
        post_body = thing.find('div', class_='usertext-body')
        content = ""
        if post_body:
            content = self.text_processor.clean_text(post_body.get_text())

        # Comments
        comments_area = soup.find('div', class_='commentarea')
        comments = []

        if comments_area:
            comment_divs = comments_area.find_all('div', class_='usertext-body', limit=50)
            for comment_div in comment_divs:
                comment_text = self.text_processor.clean_text(comment_div.get_text())
                if comment_text and len(comment_text) > 20:
                    comments.append(comment_text)

        # Combine post and valuable comments
        full_content = f"Title: {title}\n\nPost: {content}\n\n"
        if comments:
            full_content += "Top Comments:\n" + "\n\n---\n\n".join(comments[:10])

        if not full_content or len(full_content) < 100:
            return None

        # Timestamp
        time_tag = thing.find('time')
        timestamp = time_tag.get('datetime', '') if time_tag else ""

        # Build post data
        post_data = {
            'url': url.replace('old.reddit.com', 'reddit.com'),  # Normalize URL
            'title': title,
            'author': author,
            'subreddit': subreddit,
            'score': score,
            'content': full_content,
            'post_body': content,
            'num_comments': len(comments),
            'top_comments': comments[:10],
            'published_date': timestamp,
            'source': 'reddit',
            'content_type': 'discussion',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'word_count': len(full_content.split()),
            'platform': 'Reddit'
        }

        # Save as JSONL
        self.save_as_jsonl(post_data)

        # Save to database
        self.storage.save_content(
            url=post_data['url'],
            title=title,
            content=full_content,
            content_type='discussion',
            source='reddit_marketing',
            author=author,
            published_date=timestamp,
            metadata=post_data,
            keywords=[subreddit, 'reddit', 'marketing']
        )

        self.mark_scraped(url)
        return post_data

    def save_as_jsonl(self, post: Dict, output_file: str = "data/reddit_marketing.jsonl"):
        """Save post as JSONL"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(post, ensure_ascii=False) + '\n')

    def scrape(self):
        """Main scraping method"""
        self.logger.info("Starting Reddit marketing content scrape")

        start_time = time.time()
        all_urls = []

        # Collect URLs from subreddits
        for subreddit in self.subreddits:
            if len(all_urls) >= self.max_posts:
                break

            try:
                # Get top posts
                urls = self.scrape_subreddit(subreddit, sort='top', time_filter='all', limit=30)
                all_urls.extend(urls)

                # Get some hot/recent posts too
                if len(all_urls) < self.max_posts:
                    urls = self.scrape_subreddit(subreddit, sort='hot', limit=20)
                    all_urls.extend(urls)

            except Exception as e:
                self.logger.error(f"Error scraping r/{subreddit}: {e}")

        # Remove duplicates
        all_urls = list(set(all_urls))[:self.max_posts]

        self.logger.info(f"Total unique posts to scrape: {len(all_urls)}")

        # Scrape posts
        successful = 0
        failed = 0

        for i, url in enumerate(all_urls, 1):
            self.logger.info(f"Scraping post {i}/{len(all_urls)}")

            try:
                post = self.scrape_post(url)
                if post:
                    successful += 1
                    self.logger.info(f"Saved: {post['title'][:60]}... ({post['word_count']} words)")
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                failed += 1

            # Progress update
            if i % 25 == 0:
                stats = self.storage.get_statistics()
                self.logger.info(f"Progress: {i}/{len(all_urls)} | {stats['total_size_mb']:.2f} MB")

        duration = time.time() - start_time

        self.logger.info(f"\nReddit scraping complete!")
        self.logger.info(f"Posts collected: {successful}")
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

    scraper = RedditMarketingScraper(max_posts=500)
    scraper.scrape()

#!/usr/bin/env python3
"""
GitHub Marketing Content from Awesome Lists
Strategy: Scrape awesome-* lists, extract GitHub repo links, then scrape those repos extensively
"""

import requests
import time
import json
import re
from pathlib import Path
from typing import List, Dict, Set
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AwesomeListGitHubScraper:
    """Scrapes GitHub repos from awesome lists, then scrapes those repos"""

    def __init__(self, rate_limit: float = 1.0):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.rate_limit = rate_limit
        self.scraped_repos = set()

        # Known awesome lists related to marketing, business, startup
        self.awesome_lists = [
            'Awesome-SEO/seo-case-studies',
            'gokepelemo/awesome-marketing',
            'ronakganatra/awesome-marketing',
            'EdoStra/Marketing-for-Founders',
            'LisaDziuba/Marketing-for-Engineers',
            'bayandin/awesome-awesomeness',  # Meta list
            'sindresorhus/awesome',  # Meta list
            'lockys/awesome-growth-hacking',
            'onurakpolat/awesome-analytics',
            'ziadoz/awesome-php',  # Has business sections
            'dypsilon/frontend-dev-bookmarks',  # Has marketing tools
            'wasabeef/awesome-android-ui',  # Design inspiration
            'junhey/awesome-startup',
            'KrishMunot/awesome-startup',
            'steve-vincent/awesome-decentralized',
            'qazbnm456/awesome-cve-poc',
           'nicejade/nice-front-end-tutorials',  # Many marketing articles
        ]

    def extract_github_repos_from_readme(self, readme_content: str) -> Set[str]:
        """Extract GitHub repository URLs from README content"""
        repos = set()

        # Pattern to match GitHub URLs
        github_patterns = [
            r'https?://github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)',
            r'\[.*?\]\(https?://github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)\)',
        ]

        for pattern in github_patterns:
            matches = re.findall(pattern, readme_content)
            for match in matches:
                # Clean up the repo path
                repo = match.strip().rstrip('/')
                # Remove anchor links and query params
                repo = re.sub(r'[#?].*$', '', repo)
                # Only add if it looks like a valid repo (has owner/name format)
                if '/' in repo and len(repo.split('/')) == 2:
                    repos.add(repo)

        return repos

    def fetch_readme(self, repo: str) -> str:
        """Fetch README content from a repository"""
        for branch in ['main', 'master']:
            try:
                url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    time.sleep(self.rate_limit)
                    return response.text

            except Exception as e:
                logger.debug(f"Error fetching README for {repo}/{branch}: {e}")

        return ""

    def scrape_repo_content(self, repo: str) -> List[Dict]:
        """Scrape all content from a repository"""
        content_items = []

        # Skip if already scraped
        if repo in self.scraped_repos:
            return content_items

        self.scraped_repos.add(repo)

        # 1. Scrape README
        for branch in ['main', 'master']:
            try:
                url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    content = response.text

                    if len(content) > 300:
                        content_items.append({
                            'repo': repo,
                            'type': 'github_readme',
                            'title': f'{repo} - README',
                            'content': content,
                            'url': f'https://github.com/{repo}',
                            'word_count': len(content.split()),
                            'source': 'github',
                            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        break

                time.sleep(self.rate_limit)

            except Exception as e:
                logger.debug(f"Error scraping README for {repo}/{branch}: {e}")

        # 2. Scrape common doc files
        doc_files = [
            'GUIDE.md', 'CONTRIBUTING.md', 'TUTORIAL.md', 'EXAMPLES.md',
            'docs/README.md', 'docs/guide.md', 'docs/getting-started.md',
            'doc/README.md', 'DOCUMENTATION.md', 'USAGE.md'
        ]

        for doc_file in doc_files:
            for branch in ['main', 'master']:
                try:
                    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{doc_file}"
                    response = self.session.get(url, timeout=15)

                    if response.status_code == 200:
                        content = response.text

                        if len(content) > 300:
                            content_items.append({
                                'repo': repo,
                                'type': 'github_docs',
                                'title': f'{repo} - {doc_file}',
                                'content': content,
                                'url': f'https://github.com/{repo}/blob/{branch}/{doc_file}',
                                'word_count': len(content.split()),
                                'source': 'github',
                                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                            })
                            break

                    time.sleep(self.rate_limit * 0.5)

                except Exception as e:
                    continue

        return content_items

    def save_to_jsonl(self, item: Dict, output_file: str = "data/github_marketing_extensive.jsonl"):
        """Save item to JSONL file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def scrape_all(self, max_repos: int = 1000):
        """Main scraping method"""
        logger.info("="*80)
        logger.info("GITHUB MARKETING CONTENT FROM AWESOME LISTS")
        logger.info("="*80)
        logger.info(f"Starting with {len(self.awesome_lists)} awesome lists")
        logger.info(f"Target: {max_repos} repositories")
        logger.info("="*80 + "\n")

        all_repos = set()
        total_items = 0
        total_words = 0

        # Step 1: Extract repo links from awesome lists
        logger.info("Step 1: Extracting repository links from awesome lists...")
        for awesome_repo in self.awesome_lists:
            logger.info(f"Processing awesome list: {awesome_repo}")

            readme = self.fetch_readme(awesome_repo)
            if readme:
                repos = self.extract_github_repos_from_readme(readme)
                all_repos.update(repos)
                logger.info(f"  Found {len(repos)} repos (total unique: {len(all_repos)})")

                # Also save the awesome list itself
                content_items = self.scrape_repo_content(awesome_repo)
                for item in content_items:
                    self.save_to_jsonl(item)
                    total_items += 1
                    total_words += item['word_count']

        # Convert to list and limit
        all_repos = list(all_repos)[:max_repos]

        logger.info(f"\n{'='*80}")
        logger.info(f"Step 2: Scraping content from {len(all_repos)} repositories...")
        logger.info(f"{'='*80}\n")

        # Step 2: Scrape content from each repo
        for i, repo in enumerate(all_repos, 1):
            logger.info(f"[{i}/{len(all_repos)}] {repo}")

            try:
                content_items = self.scrape_repo_content(repo)

                for item in content_items:
                    self.save_to_jsonl(item)
                    total_items += 1
                    total_words += item['word_count']

                if content_items:
                    total_content_words = sum(item['word_count'] for item in content_items)
                    logger.info(f"  ✓ Collected {len(content_items)} files, {total_content_words:,} words")
                else:
                    logger.info(f"  ⊘ No content")

            except Exception as e:
                logger.error(f"  ✗ Error: {e}")

            # Progress update
            if i % 50 == 0:
                size_mb = Path('data/github_marketing_extensive.jsonl').stat().st_size / (1024 * 1024) if Path('data/github_marketing_extensive.jsonl').exists() else 0
                logger.info(f"\n--- Progress: {i}/{len(all_repos)} | {total_items} items | {total_words:,} words | {size_mb:.2f} MB ---\n")

        # Final stats
        logger.info(f"\n{'='*80}")
        logger.info("SCRAPING COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Repositories scraped: {len(self.scraped_repos)}")
        logger.info(f"Total items: {total_items}")
        logger.info(f"Total words: {total_words:,}")

        if Path('data/github_marketing_extensive.jsonl').exists():
            size_mb = Path('data/github_marketing_extensive.jsonl').stat().st_size / (1024 * 1024)
            size_gb = size_mb / 1024
            logger.info(f"File size: {size_mb:.2f} MB ({size_gb:.3f} GB)")

            with open('data/github_marketing_extensive.jsonl', 'r') as f:
                line_count = sum(1 for _ in f)
            logger.info(f"Items in file: {line_count}")

        logger.info(f"{'='*80}")

        return {
            'repos_scraped': len(self.scraped_repos),
            'items': total_items,
            'words': total_words,
            'size_mb': size_mb,
            'size_gb': size_gb
        }


if __name__ == '__main__':
    scraper = AwesomeListGitHubScraper(rate_limit=0.8)
    scraper.scrape_all(max_repos=1000)

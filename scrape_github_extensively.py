#!/usr/bin/env python3
"""
Extensive GitHub Marketing Content Scraper
Since regular websites block with 403, scrape GitHub extensively for marketing content.
GitHub has tons of real human-written marketing guides, case studies, and resources.
"""

import requests
import time
import json
import re
from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExtensiveGitHubMarketingScraper:
    """Scrapes GitHub extensively for marketing-related content"""

    def __init__(self, rate_limit: float = 1.5):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        self.rate_limit = rate_limit
        self.collected_content = []

        # Marketing search queries for GitHub
        self.search_queries = [
            'marketing strategy', 'brand building', 'marketing campaigns',
            'case studies marketing', 'digital marketing', 'content marketing',
            'social media marketing', 'email marketing', 'SEO guide',
            'growth hacking', 'marketing resources', 'brand strategy',
            'marketing playbook', 'startup marketing', 'product marketing',
            'marketing framework', 'advertising', 'branding guide',
            'marketing analytics', 'customer acquisition', 'viral marketing',
            'influencer marketing', 'marketing automation', 'conversion optimization',
            'marketing tactics', 'brand identity', 'marketing templates'
        ]

    def search_github_repos(self, query: str, max_repos: int = 50) -> List[str]:
        """Search GitHub for repositories matching query"""
        repos = []

        try:
            # Use GitHub search page
            search_url = f"https://github.com/search?q={query.replace(' ', '+')}&type=repositories&s=stars&o=desc"

            logger.info(f"Searching GitHub: {query}")
            response = self.session.get(search_url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find repository links
                repo_links = soup.find_all('a', class_=re.compile(r'v-align-middle'))

                for link in repo_links[:max_repos]:
                    href = link.get('href', '')
                    if href.startswith('/') and href.count('/') == 2:
                        repo = href.strip('/')
                        if repo not in repos:
                            repos.append(repo)

            time.sleep(self.rate_limit)

        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")

        return repos

    def scrape_repo_readme(self, repo: str) -> Dict:
        """Scrape README from repository"""
        for branch in ['main', 'master']:
            try:
                url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    content = response.text

                    # Only save if substantial content
                    if len(content) > 500:
                        return {
                            'repo': repo,
                            'type': 'github_readme',
                            'title': f'{repo} - README',
                            'content': content,
                            'url': f'https://github.com/{repo}',
                            'word_count': len(content.split()),
                            'source': 'github',
                            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                        }

                time.sleep(self.rate_limit)

            except Exception as e:
                logger.debug(f"Error fetching README for {repo}/{branch}: {e}")
                continue

        return None

    def scrape_repo_wiki(self, repo: str) -> List[Dict]:
        """Scrape wiki pages from repository if available"""
        wiki_pages = []

        try:
            # Check if wiki exists
            wiki_url = f"https://github.com/{repo}/wiki"
            response = self.session.get(wiki_url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find wiki page links
                wiki_links = soup.find_all('a', href=re.compile(r'/' + re.escape(repo) + r'/wiki/[^/]+$'))

                for link in wiki_links[:10]:  # Limit to 10 wiki pages per repo
                    page_url = 'https://github.com' + link.get('href')

                    try:
                        page_response = self.session.get(page_url, timeout=30)
                        if page_response.status_code == 200:
                            page_soup = BeautifulSoup(page_response.text, 'html.parser')

                            # Extract wiki content
                            wiki_body = page_soup.find('div', class_=re.compile(r'markdown-body'))
                            if wiki_body:
                                content = wiki_body.get_text(separator='\n', strip=True)

                                if len(content) > 300:
                                    wiki_pages.append({
                                        'repo': repo,
                                        'type': 'github_wiki',
                                        'title': link.get_text(strip=True),
                                        'content': content,
                                        'url': page_url,
                                        'word_count': len(content.split()),
                                        'source': 'github',
                                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                                    })

                        time.sleep(self.rate_limit)
                    except Exception as e:
                        logger.debug(f"Error scraping wiki page {page_url}: {e}")

            time.sleep(self.rate_limit)

        except Exception as e:
            logger.debug(f"No wiki or error for {repo}: {e}")

        return wiki_pages

    def scrape_repo_docs(self, repo: str) -> List[Dict]:
        """Scrape documentation markdown files"""
        docs = []

        # Common doc file locations
        doc_paths = [
            'GUIDE.md', 'CONTRIBUTING.md', 'DOCUMENTATION.md',
            'docs/README.md', 'docs/guide.md', 'docs/index.md',
            'doc/README.md', 'TUTORIAL.md', 'EXAMPLES.md'
        ]

        for doc_path in doc_paths:
            for branch in ['main', 'master']:
                try:
                    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{doc_path}"
                    response = self.session.get(url, timeout=30)

                    if response.status_code == 200:
                        content = response.text

                        if len(content) > 300:
                            docs.append({
                                'repo': repo,
                                'type': 'github_docs',
                                'title': f'{repo} - {doc_path}',
                                'content': content,
                                'url': f'https://github.com/{repo}/blob/{branch}/{doc_path}',
                                'word_count': len(content.split()),
                                'source': 'github',
                                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                            })
                            break  # Found it in this branch

                    time.sleep(self.rate_limit / 2)  # Faster for docs

                except Exception as e:
                    continue

        return docs

    def save_to_jsonl(self, item: Dict, output_file: str = "data/github_marketing_extensive.jsonl"):
        """Save item to JSONL file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    def scrape_all(self, repos_per_query: int = 30, max_total_repos: int = 500):
        """Main scraping method"""
        logger.info("="*80)
        logger.info("EXTENSIVE GITHUB MARKETING CONTENT SCRAPER")
        logger.info("="*80)
        logger.info(f"Search queries: {len(self.search_queries)}")
        logger.info(f"Target repos: {max_total_repos}")
        logger.info("="*80 + "\n")

        all_repos = set()
        total_items = 0
        total_words = 0

        # Step 1: Collect repos from all search queries
        for query in self.search_queries:
            if len(all_repos) >= max_total_repos:
                break

            repos = self.search_github_repos(query, max_repos=repos_per_query)
            all_repos.update(repos)
            logger.info(f"Found {len(repos)} repos for '{query}' (total unique: {len(all_repos)})")

        all_repos = list(all_repos)[:max_total_repos]

        logger.info(f"\n{'='*80}")
        logger.info(f"Collected {len(all_repos)} unique repositories")
        logger.info(f"Now scraping content from each repo...")
        logger.info(f"{'='*80}\n")

        # Step 2: Scrape content from each repo
        for i, repo in enumerate(all_repos, 1):
            logger.info(f"\n[{i}/{len(all_repos)}] Processing: {repo}")

            try:
                # Scrape README
                readme = self.scrape_repo_readme(repo)
                if readme:
                    self.save_to_jsonl(readme)
                    total_items += 1
                    total_words += readme['word_count']
                    logger.info(f"  ✓ README: {readme['word_count']} words")

                # Scrape Wiki pages
                wiki_pages = self.scrape_repo_wiki(repo)
                for wiki in wiki_pages:
                    self.save_to_jsonl(wiki)
                    total_items += 1
                    total_words += wiki['word_count']
                if wiki_pages:
                    logger.info(f"  ✓ Wiki: {len(wiki_pages)} pages, {sum(w['word_count'] for w in wiki_pages)} words")

                # Scrape additional docs
                docs = self.scrape_repo_docs(repo)
                for doc in docs:
                    self.save_to_jsonl(doc)
                    total_items += 1
                    total_words += doc['word_count']
                if docs:
                    logger.info(f"  ✓ Docs: {len(docs)} files, {sum(d['word_count'] for d in docs)} words")

            except Exception as e:
                logger.error(f"  ✗ Error processing {repo}: {e}")

            # Progress update
            if i % 25 == 0:
                size_mb = Path('data/github_marketing_extensive.jsonl').stat().st_size / (1024 * 1024) if Path('data/github_marketing_extensive.jsonl').exists() else 0
                logger.info(f"\n--- Progress: {i}/{len(all_repos)} repos | {total_items} items | {total_words:,} words | {size_mb:.2f} MB ---\n")

        # Final stats
        logger.info(f"\n{'='*80}")
        logger.info("SCRAPING COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Repositories processed: {len(all_repos)}")
        logger.info(f"Total items collected: {total_items}")
        logger.info(f"Total words: {total_words:,}")

        if Path('data/github_marketing_extensive.jsonl').exists():
            size_mb = Path('data/github_marketing_extensive.jsonl').stat().st_size / (1024 * 1024)
            size_gb = size_mb / 1024
            logger.info(f"File size: {size_mb:.2f} MB ({size_gb:.3f} GB)")

            with open('data/github_marketing_extensive.jsonl', 'r') as f:
                line_count = sum(1 for _ in f)
            logger.info(f"Items in file: {line_count}")

        logger.info(f"{'='*80}")


if __name__ == '__main__':
    scraper = ExtensiveGitHubMarketingScraper(rate_limit=1.5)
    scraper.scrape_all(repos_per_query=30, max_total_repos=500)

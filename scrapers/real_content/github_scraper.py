"""
GitHub Marketing Content Scraper
Scrapes real marketing case studies and resources from GitHub repositories.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubMarketingScraper:
    """Scrapes marketing content from GitHub repositories"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })

        # Target repositories
        self.repos = [
            'Awesome-SEO/seo-case-studies',
            'gokepelemo/awesome-marketing',
            'ronakganatra/awesome-marketing',
            'marketingtoolslist/awesome-marketing',
            'EdoStra/Marketing-for-Founders',
        ]

    def scrape_repo_readme(self, repo: str) -> Dict:
        """Scrape README from GitHub repo"""
        url = f"https://raw.githubusercontent.com/{repo}/main/README.md"

        # Try main branch first, then master
        for branch in ['main', 'master']:
            try:
                url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
                response = self.session.get(url, timeout=30)

                if response.status_code == 200:
                    logger.info(f"✓ Scraped {repo}")
                    return {
                        'repo': repo,
                        'content': response.text,
                        'url': f"https://github.com/{repo}",
                        'branch': branch
                    }
            except Exception as e:
                logger.error(f"Error scraping {repo} ({branch}): {e}")

        return None

    def extract_links_from_markdown(self, markdown: str) -> List[Dict]:
        """Extract all links from markdown content"""
        # Pattern for markdown links: [text](url)
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(pattern, markdown)

        links = []
        for text, url in matches:
            # Filter for relevant marketing content
            if any(keyword in text.lower() or keyword in url.lower() for keyword in [
                'case study', 'case-study', 'marketing', 'seo', 'content',
                'strategy', 'growth', 'campaign', 'blog', 'article', 'guide'
            ]):
                links.append({'title': text.strip(), 'url': url.strip()})

        return links

    def scrape_all_repos(self) -> List[Dict]:
        """Scrape all GitHub repositories"""
        all_data = []

        for repo in self.repos:
            logger.info(f"Scraping repository: {repo}")
            data = self.scrape_repo_readme(repo)

            if data:
                # Extract links from the README
                links = self.extract_links_from_markdown(data['content'])
                data['extracted_links'] = links
                data['link_count'] = len(links)
                all_data.append(data)

                logger.info(f"  Found {len(links)} marketing-related links")

                # Save to JSONL
                self.save_jsonl(data, 'data/github_marketing_repos.jsonl')

            time.sleep(1)  # Be nice to GitHub

        return all_data

    def save_jsonl(self, data: Dict, filename: str):
        """Save data as JSONL"""
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    scraper = GitHubMarketingScraper()
    results = scraper.scrape_all_repos()

    logger.info(f"\n{'='*60}")
    logger.info(f"Scraped {len(results)} repositories")
    total_links = sum(r['link_count'] for r in results)
    logger.info(f"Found {total_links} total marketing links")
    logger.info(f"{'='*60}")

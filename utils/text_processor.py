"""
Text Processing Utilities
Clean and process scraped text content.
"""

import re
from typing import List, Dict
from bs4 import BeautifulSoup
import html2text


class TextProcessor:
    """
    Handles text cleaning, extraction, and processing.
    """

    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.body_width = 0  # Don't wrap text

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def html_to_markdown(self, html: str) -> str:
        """
        Convert HTML to Markdown.

        Args:
            html: HTML content

        Returns:
            Markdown formatted text
        """
        return self.html_converter.handle(html)

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main content from HTML, removing navigation, ads, etc.

        Args:
            soup: BeautifulSoup object

        Returns:
            Main content text
        """
        # Remove unwanted elements
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove common ad/navigation classes
        unwanted_classes = [
            'ad', 'advertisement', 'sidebar', 'menu', 'navigation',
            'footer', 'header', 'cookie', 'popup', 'modal', 'social-share'
        ]

        for class_name in unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()

        # Try to find main content area
        main_content = (
            soup.find('article') or
            soup.find('main') or
            soup.find('div', class_=re.compile('content|post|article', re.I)) or
            soup.find('body')
        )

        if main_content:
            return self.clean_text(main_content.get_text())

        return ""

    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract potential keywords from text.

        Args:
            text: Text to analyze
            min_length: Minimum word length

        Returns:
            List of potential keywords
        """
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + r',}\b', text.lower())

        # Filter out common words (basic stop words)
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day',
            'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now',
            'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its',
            'let', 'put', 'say', 'she', 'too', 'use', 'this', 'that',
            'with', 'have', 'from', 'they', 'were', 'been', 'have',
            'their', 'what', 'about', 'would', 'there', 'when', 'your'
        }

        keywords = [w for w in words if w not in stop_words]

        # Count frequency and return unique
        from collections import Counter
        counter = Counter(keywords)
        return [word for word, count in counter.most_common(50)]

    def truncate_text(self, text: str, max_length: int = 500) -> str:
        """
        Truncate text to a maximum length.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        return text[:max_length].rsplit(' ', 1)[0] + '...'

    def extract_urls(self, text: str) -> List[str]:
        """
        Extract URLs from text.

        Args:
            text: Text containing URLs

        Returns:
            List of URLs
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)

    def remove_html_tags(self, text: str) -> str:
        """
        Remove all HTML tags from text.

        Args:
            text: Text with HTML tags

        Returns:
            Plain text
        """
        return BeautifulSoup(text, 'lxml').get_text()

    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize all whitespace in text.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        return ' '.join(text.split())

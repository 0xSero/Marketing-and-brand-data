"""
Storage Utilities
Handle data persistence and indexing.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


class DataStorage:
    """
    Manages data storage using SQLite and file system.
    """

    def __init__(self, db_path: str = "data/index/knowledge_base.db"):
        """
        Initialize storage.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Articles/Content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_hash TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                content_type TEXT,
                source TEXT,
                author TEXT,
                published_date TEXT,
                scraped_date TEXT,
                content_preview TEXT,
                full_content_path TEXT,
                metadata_json TEXT,
                word_count INTEGER,
                size_bytes INTEGER,
                keywords TEXT
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON content(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_type ON content(content_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scraped_date ON content(scraped_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_url_hash ON content(url_hash)')

        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scraper_name TEXT,
                run_date TEXT,
                total_items INTEGER,
                successful_items INTEGER,
                failed_items INTEGER,
                total_size_bytes INTEGER,
                duration_seconds REAL,
                metadata_json TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_url_hash(self, url: str) -> str:
        """Generate hash for URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def content_exists(self, url: str) -> bool:
        """Check if content already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        url_hash = self.get_url_hash(url)
        cursor.execute('SELECT id FROM content WHERE url_hash = ?', (url_hash,))
        exists = cursor.fetchone() is not None

        conn.close()
        return exists

    def save_content(
        self,
        url: str,
        title: str,
        content: str,
        content_type: str,
        source: str,
        author: str = "",
        published_date: str = "",
        metadata: Optional[Dict] = None,
        keywords: Optional[List[str]] = None
    ) -> int:
        """
        Save content to database and file system.

        Args:
            url: Content URL
            title: Content title
            content: Full content text
            content_type: Type (article, case_study, etc.)
            source: Source name
            author: Author name
            published_date: Publication date
            metadata: Additional metadata
            keywords: List of keywords

        Returns:
            Content ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        url_hash = self.get_url_hash(url)
        scraped_date = datetime.now().isoformat()

        # Save full content to file
        content_dir = Path("data/processed") / source / content_type
        content_dir.mkdir(parents=True, exist_ok=True)

        content_filename = f"{url_hash}.txt"
        content_path = content_dir / content_filename

        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Calculate statistics
        word_count = len(content.split())
        size_bytes = len(content.encode('utf-8'))
        content_preview = content[:500]

        # Prepare data
        keywords_str = ','.join(keywords) if keywords else ""
        metadata_json = json.dumps(metadata) if metadata else "{}"

        # Insert into database
        cursor.execute('''
            INSERT OR REPLACE INTO content (
                url_hash, url, title, content_type, source, author,
                published_date, scraped_date, content_preview,
                full_content_path, metadata_json, word_count,
                size_bytes, keywords
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            url_hash, url, title, content_type, source, author,
            published_date, scraped_date, content_preview,
            str(content_path), metadata_json, word_count,
            size_bytes, keywords_str
        ))

        content_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return content_id

    def get_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve content by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return dict(row)
        return None

    def search_content(
        self,
        query: str = "",
        source: str = "",
        content_type: str = "",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search content in database.

        Args:
            query: Search query (searches title and preview)
            source: Filter by source
            content_type: Filter by content type
            limit: Maximum results

        Returns:
            List of matching content
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql = 'SELECT * FROM content WHERE 1=1'
        params = []

        if query:
            sql += ' AND (title LIKE ? OR content_preview LIKE ? OR keywords LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])

        if source:
            sql += ' AND source = ?'
            params.append(source)

        if content_type:
            sql += ' AND content_type = ?'
            params.append(content_type)

        sql += ' ORDER BY scraped_date DESC LIMIT ?'
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        conn.close()

        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total content count
        cursor.execute('SELECT COUNT(*) FROM content')
        stats['total_items'] = cursor.fetchone()[0]

        # Count by source
        cursor.execute('SELECT source, COUNT(*) FROM content GROUP BY source')
        stats['by_source'] = dict(cursor.fetchall())

        # Count by content type
        cursor.execute('SELECT content_type, COUNT(*) FROM content GROUP BY content_type')
        stats['by_type'] = dict(cursor.fetchall())

        # Total size
        cursor.execute('SELECT SUM(size_bytes) FROM content')
        total_bytes = cursor.fetchone()[0] or 0
        stats['total_size_bytes'] = total_bytes
        stats['total_size_mb'] = round(total_bytes / (1024 * 1024), 2)
        stats['total_size_gb'] = round(total_bytes / (1024 * 1024 * 1024), 3)

        # Total words
        cursor.execute('SELECT SUM(word_count) FROM content')
        stats['total_words'] = cursor.fetchone()[0] or 0

        conn.close()

        return stats

    def save_scraping_run(
        self,
        scraper_name: str,
        total_items: int,
        successful_items: int,
        failed_items: int,
        total_size_bytes: int,
        duration_seconds: float,
        metadata: Optional[Dict] = None
    ):
        """Save statistics for a scraping run"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO scraping_stats (
                scraper_name, run_date, total_items, successful_items,
                failed_items, total_size_bytes, duration_seconds, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scraper_name,
            datetime.now().isoformat(),
            total_items,
            successful_items,
            failed_items,
            total_size_bytes,
            duration_seconds,
            json.dumps(metadata) if metadata else "{}"
        ))

        conn.commit()
        conn.close()

    def export_to_json(self, output_file: str):
        """Export all content metadata to JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM content')
        rows = cursor.fetchall()

        data = [dict(row) for row in rows]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        conn.close()

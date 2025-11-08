# Marketing Knowledge Database Scraper

A comprehensive web scraping system designed to collect and organize gigabytes of marketing knowledge from across the internet, including blog posts, case studies, news articles, brand strategy content, and campaign information.

## Overview

This project scrapes high-quality marketing content from multiple authoritative sources and stores it in a searchable database. The system is designed to collect **2+ GB** of marketing knowledge while respecting ethical scraping practices.

## Features

- **Multi-Source Scraping**: Automatically scrapes 15+ marketing websites
- **Ethical Scraping**: Respects robots.txt, implements rate limiting, and uses proper retry logic
- **Intelligent Storage**: SQLite database with full-text search capabilities
- **Content Processing**: Automated text cleaning, keyword extraction, and metadata collection
- **Progress Tracking**: Real-time logging and progress monitoring
- **Deduplication**: Prevents duplicate content collection
- **Modular Design**: Easy to add new sources or customize existing scrapers

## Data Sources

### Marketing Blogs (7 sources)
- **HubSpot Blog** - Marketing, sales, and service content
- **Neil Patel** - SEO and content marketing insights
- **Moz Blog** - SEO expertise and best practices
- **Content Marketing Institute** - Content strategy and tactics
- **MarketingProfs** - Marketing know-how
- **Copyblogger** - Content marketing and copywriting
- **Search Engine Land** - Search marketing news

### Case Studies (3 sources)
- **Think with Google** - Google's marketing case studies
- **HubSpot Case Studies** - Customer success stories
- **Marketo Case Studies** - Marketing automation examples

### Marketing News (5 sources)
- **AdAge** - Advertising and marketing news
- **Marketing Week** - Marketing industry insights
- **The Drum** - Marketing and media news
- **Adweek** - Advertising and marketing news
- **Campaign Live** - Global marketing news

## Project Structure

```
Marketing-and-brand-data/
├── scrapers/                      # Scraper modules
│   ├── base_scraper.py           # Base scraper class with ethical practices
│   ├── blog_scrapers/            # Blog-specific scrapers
│   │   ├── generic_blog_scraper.py
│   │   └── marketing_blogs_scraper.py
│   ├── casestudy_scrapers/       # Case study scrapers
│   │   └── casestudy_scraper.py
│   └── news_scrapers/            # News scrapers
│       └── marketing_news_scraper.py
├── utils/                         # Utility modules
│   ├── text_processor.py         # Text cleaning and processing
│   ├── storage.py                # Database and file storage
│   └── rate_limiter.py           # Rate limiting utilities
├── config/                        # Configuration files
│   └── sources.json              # Source configurations
├── data/                          # Data storage
│   ├── raw/                      # Raw scraped data by source
│   ├── processed/                # Processed content
│   └── index/                    # SQLite database
├── logs/                          # Log files
├── main.py                        # Main orchestrator
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- 5+ GB free disk space

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Marketing-and-brand-data
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Scrape all sources (blogs, case studies, news):
```bash
python main.py --all
```

### Selective Scraping

Scrape only blogs:
```bash
python main.py --blogs
```

Scrape only case studies:
```bash
python main.py --case-studies
```

Scrape only news:
```bash
python main.py --news
```

### Database Operations

View statistics:
```bash
python main.py --stats
```

Export database to JSON:
```bash
python main.py --export output.json
```

### Advanced Options

Use custom configuration:
```bash
python main.py --all --config custom_config.json
```

Specify log file:
```bash
python main.py --all --log-file my_scrape.log
```

## Configuration

Edit `config/sources.json` to customize scraping behavior:

```json
{
  "target_size_gb": 2.0,
  "rate_limit_seconds": 2.0,

  "scrapers": {
    "blogs": {
      "enabled": true,
      "max_articles_per_source": 500
    }
  }
}
```

### Key Configuration Options

- **target_size_gb**: Target data collection size
- **rate_limit_seconds**: Delay between requests
- **max_articles_per_source**: Maximum articles per source
- **enabled**: Enable/disable scraper categories

## Database Schema

The SQLite database (`data/index/knowledge_base.db`) contains:

### Content Table
- **id**: Unique identifier
- **url**: Original URL
- **title**: Content title
- **content_type**: Type (article, case_study, news)
- **source**: Source name
- **author**: Author name
- **published_date**: Publication date
- **scraped_date**: Scraping timestamp
- **content_preview**: First 500 characters
- **full_content_path**: Path to full content file
- **metadata_json**: Additional metadata
- **word_count**: Number of words
- **size_bytes**: Content size
- **keywords**: Extracted keywords

### Querying the Database

```python
from utils.storage import DataStorage

storage = DataStorage()

# Search for content
results = storage.search_content(
    query="brand strategy",
    content_type="article",
    limit=50
)

# Get statistics
stats = storage.get_statistics()
print(f"Total items: {stats['total_items']}")
print(f"Total size: {stats['total_size_gb']} GB")
```

## Ethical Scraping Practices

This project follows strict ethical scraping guidelines:

1. **Robots.txt Compliance**: Always respects robots.txt directives
2. **Rate Limiting**: 2-second delay between requests (configurable)
3. **User-Agent**: Identifies as a bot with contact information
4. **Retry Logic**: Exponential backoff for failed requests
5. **Public Content Only**: Only scrapes publicly available content
6. **No Server Strain**: Conservative request rates to avoid impacting servers
7. **Attribution**: Preserves original URLs and metadata

## Performance

### Expected Results

With default settings, you can expect:

- **Total Items**: 3,000-5,000 articles/case studies/news items
- **Total Size**: 2-3 GB of text content
- **Runtime**: 2-6 hours (depending on rate limits and network speed)
- **Success Rate**: 85-95% (some sources may block or rate-limit)

### Optimization Tips

1. **Parallel Processing**: Run different scraper categories separately
2. **Resume Capability**: Interrupted scrapes can be resumed (progress is saved)
3. **Selective Scraping**: Focus on specific sources for faster results
4. **Rate Limit Tuning**: Increase `rate_limit_seconds` if experiencing blocks

## Troubleshooting

### Common Issues

**Problem**: "Robots.txt disallows fetching"
- **Solution**: Some sites may block scraping. This is intentional and respected.

**Problem**: "Failed to fetch after 3 attempts"
- **Solution**: Network issues or rate limiting. The scraper will continue with other content.

**Problem**: Slow scraping speed
- **Solution**: This is intentional to respect servers. Consider reducing `max_articles_per_source`.

**Problem**: Database locked error
- **Solution**: Ensure only one scraper instance is running at a time.

### Logs

All scraping activity is logged to:
- Console output (real-time)
- `logs/scraper_YYYYMMDD_HHMMSS.log` (persistent)

Check logs for detailed error messages and progress information.

## Extending the System

### Adding a New Source

1. Create a new scraper in the appropriate directory
2. Extend `BaseScraper` or use `GenericBlogScraper`
3. Add configuration to relevant config file
4. Update the orchestrator to include the new scraper

Example:

```python
from scrapers.base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def scrape(self):
        # Implement scraping logic
        pass
```

### Custom Content Processing

Modify `utils/text_processor.py` to add custom text processing:

```python
def custom_extraction(self, soup):
    # Your custom logic here
    pass
```

## Data Analysis

### Using the Data

The collected data can be used for:

1. **Training AI Models**: Use as training data for marketing-focused LLMs
2. **Research**: Analyze marketing trends and best practices
3. **Knowledge Base**: Build a searchable marketing knowledge repository
4. **Content Analysis**: Study successful campaigns and strategies

### Export Formats

- **SQLite Database**: For structured queries and analysis
- **JSON**: For data interchange and processing
- **Text Files**: Individual content pieces for reading/processing

## License

This project is for educational and research purposes. Always respect the original content creators' copyright and terms of service.

## Legal and Ethical Considerations

- ✅ **Public Content Only**: Only scrapes publicly accessible content
- ✅ **Attribution**: Preserves original URLs and author information
- ✅ **Robots.txt**: Respects all robots.txt directives
- ✅ **Rate Limiting**: Conservative request rates
- ⚠️ **Personal Use**: Intended for research and personal knowledge building
- ⚠️ **Copyright**: Original content remains property of respective owners
- ⚠️ **Terms of Service**: Users should review ToS of scraped websites

## Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Add new scrapers or improve existing ones
4. Submit a pull request

## Support

For issues or questions:
- Check the logs in `logs/` directory
- Review the configuration in `config/sources.json`
- Ensure all dependencies are installed correctly

## Roadmap

Future enhancements:
- [ ] Add image downloading capability
- [ ] Implement vector embeddings for semantic search
- [ ] Add more international marketing sources
- [ ] Create web interface for browsing collected data
- [ ] Add support for PDF case studies
- [ ] Implement automatic categorization/tagging
- [ ] Add API for programmatic access

## Acknowledgments

This project scrapes content from various marketing publications and respects their robots.txt directives and rate limits. All content ownership remains with the original publishers.

---

**Built with respect for the marketing community and ethical web scraping practices.**

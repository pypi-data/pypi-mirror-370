# MarketMiner

MarketMiner is a Python library for scraping finance-related information — from market news to company fundamentals — in an easy and structured way.

It is designed for analysts, traders, and developers who want quick programmatic access to financial data without relying on expensive APIs.

## Features

- **News Scraper**: Get historical news articles from various sources.
- **Company Fundamentals**: Access financial statements and key metrics for public companies.
- **Utility Functions**: Common helpers for parsing, cleaning, and making requests.

## Installation
```bash
pip install marketminer
```

## Usage
```python
from marketminer import scrape_economic_times

df = scrape_economic_times(start_date='2023-01-01', end_date='2023-10-01')
print(df.head())
```


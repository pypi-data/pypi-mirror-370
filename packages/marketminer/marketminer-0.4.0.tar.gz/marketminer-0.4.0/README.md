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

### 1. Scraping News Articles
```python
from marketminer import scrape_economic_times

df = scrape_economic_times(start_date='2023-01-01', end_date='2023-10-01')
print(df.head())
```

### 2. Fetching Company Fundamentals
```python
from marketminer import scrape_fundamentals
financial_data = scrape_fundamentals("TCS")

print("Profit & Loss Statement:")
print(financial_data['profit_loss'].head())
print("Balance Sheet:")
print(financial_data['balance_sheet'].head())
```

## Dependencies

- `requests`: For making HTTP requests.
- `pandas`: For data manipulation and analysis.
- `beautifulsoup4`: For parsing HTML content.
- `selenium`: For web scraping dynamic content.

Note: For fundamentals scraping, ensure you have Google Chrome + ChromeDriver installed.
- Download ChromeDriver: https://chromedriver.chromium.org/downloads

## License
MIT License. Free to use and modify.
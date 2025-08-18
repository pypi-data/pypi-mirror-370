'''
Module for scraping news articles from various sources.
'''

import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd
from datetime import datetime, timedelta, date
from .utils import date_to_excel_serial
import re
from urllib.parse import urljoin
import asyncio
import aiohttp
import nest_asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/120.0.0.0 Safari/537.36"
}
_BASE = "https://economictimes.indiatimes.com"

async def fetch(session, url):
    """
    Asynchronous function to fetch a URL using aiohttp.

    Parameters:
    session (aiohttp.ClientSession): The session to use for the request.
    url (str): The URL to fetch.

    Returns:
        str: The response text.
    """
    async with session.get(url) as response:
        if response.status != 200:
            logger.warning(f"Failed to fetch {url} with status {response.status}")
            return None
        return await response.text()


def scrape_economic_times(start_date: str | datetime | date, end_date: str | datetime | date) -> pd.DataFrame:
    """
    Scrape news articles from Economic Times within a date range.

    Parameters:
    start_date (str): Start date in the format 'YYYY-MM-DD'.
    end_date (str): End date in the format 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: DataFrame containing news articles.
    """
    try:
        return asyncio.run(scrape_economic_times_async(start_date, end_date))
    except Exception as e:
        # Fix for Jupyter or interactive environments
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(scrape_economic_times_async(start_date, end_date))

async def process_article(session, article, curr_date):
    headline = article.text.strip()
    link = article.get('href', '')
    if link.startswith("/"):
        link = urljoin(_BASE, link)
    link = link.strip()

    if 'live' in link or 'articleshow' not in link:
        return None

    html = await fetch(session, link)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    match = re.search(r'/(?:amp_)?articleshow/(\d+)\.cms', link)
    article_id = match.group(1) if match else None
    body = ' '.join([p.get_text() for p in soup.select('.artText, .Normal')])

    return {
        "article_id": article_id,
        "headline": headline,
        "link": link,
        "date": curr_date.strftime("%Y-%m-%d"),
        "body": body
    }

async def scrape_economic_times_async(start_date, end_date):
    """
    Asynchronously scrape news articles from Economic Times within a date range.
    Parameters:
    start_date (str): Start date in the format 'YYYY-MM-DD'.
    end_date (str): End date in the format 'YYYY-MM-DD'.
    Returns:
        pd.DataFrame: DataFrame containing news articles.
    """
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date.")

    results = []
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        curr_date = start_dt
        while curr_date <= end_dt:
            logger.info(f"Scraping archive for {curr_date.date()}...")
            archive_url = f"{_BASE}/archivelist/year-{curr_date.year},month-{curr_date.month},starttime-{date_to_excel_serial(curr_date.date())}.cms"
            html = await fetch(session, archive_url)
            if not html:
                curr_date += timedelta(days=1)
                continue

            soup = BeautifulSoup(html, "html.parser")
            articles = soup.select("a[href*='/industry/'], a[href*='/markets/'], a[href*='/tech/']")

            tasks = [process_article(session, article, curr_date) for article in articles]
            day_results = await asyncio.gather(*tasks)
            results.extend([r for r in day_results if r])

            curr_date += timedelta(days=1)

    logging.info(f"Dropping duplicate articles based on headline and link.")
    # Convert results to DataFrame
    df = pd.DataFrame(results)
    if df.empty:
        return pd.DataFrame(columns=["headline", "link", "category", "date", "body"])

    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)
    logger.info(f"Scraped {len(df)} articles from Economic Times asynchronously.")
    return df
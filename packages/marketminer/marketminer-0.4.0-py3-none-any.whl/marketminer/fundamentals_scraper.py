'''
Module for scraping fundamental data from financial websites.
'''

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import clean_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_BASE = "https://www.screener.in/company/"

def scrape_fundamentals(ticker):
    '''
    Scrape fundamental data for a given stock ticker from Screener.in.
    Parameters:
    ticker (str): Stock ticker symbol.
    Returns:
    dict: A dictionary containing DataFrames for Profit & Loss, Balance Sheet, Cash Flow, and Ratios.

    '''
    # Provide url of screener with option to change ticker
    url = f"{_BASE}{ticker}/"
    logger.info(f"Scraping fundamentals for ticker: {ticker} from {url}")
    # Set up chrome webdriver options for headless browsing i.e new chrome tab won't open
    options = Options()
    options.add_argument("--headless")
    # Create chrome webdriver object with options
    driver = webdriver.Chrome(options=options)
    # Navigate to url
    driver.get(url)
    # Give 5 seconds to load page
    time.sleep(2.5)
    # Find all elements in the page with class 'button-plain' to expand all tables. store in a list
    expand_buttons = driver.find_elements(By.CLASS_NAME, "button-plain")
    # Wait until all elements are found
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
    # Ignoring the 1st button. click on all buttons as specified above
    for button in expand_buttons[1:]:
        driver.execute_script("arguments[0].click();", button)
        # 1 second pause to load
        time.sleep(1)
    # 2 second extra pause to ensure loading
    time.sleep(2)
    # Parse extended html content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Close chrome tab
    driver.quit()
    # scrape P&L data
    financial_table = soup.find('h2', text='Profit & Loss')
    table = financial_table.find_next('table')
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr')[1:]:
        cols = [ele.text.strip().replace(',', '') for ele in row.find_all('td')]
        rows.append(cols)
    # Store P&L data in a dataframe and clean
    pl = pd.DataFrame(rows, columns=headers)
    pl = pl.drop(columns='TTM', errors='ignore')
    pl = clean_data(pl)

    # Scrape balance sheet data
    financial_table = soup.find('h2', text='Balance Sheet')
    table = financial_table.find_next('table')
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr')[1:]:
        cols = [ele.text.strip().replace(',', '') for ele in row.find_all('td')]
        rows.append(cols)
    # Store balance sheet data in a dataframe and clean
    bs = pd.DataFrame(rows, columns=headers)
    bs = bs.drop(columns='TTM', errors='ignore')
    bs = clean_data(bs)

    # Scrape cash flow data
    financial_table = soup.find('h2', text='Cash Flows')
    table = financial_table.find_next('table')
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr')[1:]:
        cols = [ele.text.strip().replace(',', '') for ele in row.find_all('td')]
        rows.append(cols)
    # Store cashflow data in a dataframe and clean
    cf = pd.DataFrame(rows, columns=headers)
    cf = cf.drop(columns='TTM', errors='ignore')
    cf = clean_data(cf)

    # Scrape ratios data
    financial_table = soup.find('h2', text='Ratios')
    table = financial_table.find_next('table')
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr')[1:]:
        cols = [ele.text.strip().replace(',', '') for ele in row.find_all('td')]
        rows.append(cols)
    # Store ratios data in a dataframe and clean
    rd = pd.DataFrame(rows, columns=headers)
    rd = rd.drop(columns='TTM', errors='ignore')
    rd = clean_data(rd)

    # # extract market cap
    # financial_table = soup.find('div', class_='company-ratios')
    # # remove , then type cast to int and multiply by 1 crore
    # mcap = int(financial_table.find('li').text.strip().split()[-2].replace(',', '')) * 10000000
    #
    # # extract current market price
    # financial_table = soup.find('div', class_='font-size-18 strong line-height-14')
    # text = financial_table.text.strip().replace(',', '')
    # lines = text.split('\n')
    # price_line = lines[0].strip()
    # # remove comma and type cast to int
    # if price_line.startswith('₹'):
    #     cmp = int(price_line[1:].replace(',', '').strip())

    logger.info(f"Scraped data for ticker: {ticker} successfully.")
    return {
        "profit_loss": pl,
        "balance_sheet": bs,
        "cash_flows": cf,
        "ratios": rd
    }
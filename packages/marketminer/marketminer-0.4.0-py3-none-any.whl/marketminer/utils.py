'''
Module containing utility functions for the MarketMiner project.
'''

from datetime import date, datetime, timedelta
import pandas as pd

def date_to_excel_serial(dt):
    '''
    Convert a date to Excel serial date format.
    Parameters:
        dt (datetime): The date to convert.
    Returns:
        int: Excel serial date number.
    '''
    base = date(1899, 12, 31)  # Excel's base date
    serial = (dt - base).days
    if dt >= date(1900, 3, 1):
        serial += 1
    return serial

def clean_data(x):
    '''
    Clean the scraped financial data.
    Parameters:
        x (pd.DataFrame): The DataFrame containing scraped data.
    Returns:
        pd.DataFrame: Cleaned DataFrame with years as rows and values as columns.
    '''
    # Transpose data so that year are rows and values are columns
    x=x.T
    # 1st row is the new column headers
    x.columns=x.iloc[0]
    # Temp list for current index
    a=list(x.index)
    # Replace 1st index to 0
    a[0]=0
    # Remove all non-digit items from index
    a = [''.join(filter(str.isdigit, str(item))) for item in a]
    # Type cast index to int
    a = [int(item) for item in a]
    # Assign cleaned index to dataframe
    x.index = a
    # Drop the 1st row that became column headers
    x = x.drop(0)
    # Replace  , and % in the data
    x = x.replace({',': '', '%': ''}, regex=True)
    # Typecast data to numeric
    x=x.apply(pd.to_numeric)
    # Remove spaces,+,%,- in column name
    x.columns = x.columns.str.strip()
    x.columns = x.columns.str.replace(' ', '')
    x.columns = x.columns.str.replace('+', '')
    x.columns = x.columns.str.replace('%', '')
    x.columns = x.columns.str.replace('-', '')
    x.columns = x.columns.str.strip()
    return x
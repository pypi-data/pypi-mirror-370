'''
Module containing utility functions for the MarketMiner project.
'''

from datetime import date, datetime, timedelta

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
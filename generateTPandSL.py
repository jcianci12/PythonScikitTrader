import csv
import decimal
from finta import TA

import csv

import pandas as pd
from config import ORDERCSVFIELDNAMES

from get_last_ohlc_bybit import get_last_ohlc_bybit

def save_updated_prices(filename, orders):
    # Write updated data to CSV file
    with open(filename, mode='w') as file:
        writer = csv.DictWriter(file, fieldnames=ORDERCSVFIELDNAMES)
        writer.writeheader()
        writer.writerows(orders)





from finta import TA

def calculate_prices(entry_price, ohlc=[]):
    if(ohlc == None):
        ohlc =get_last_ohlc_bybit("BTCUSDT","5") 
        ohlc = ohlc.apply(pd.to_numeric, errors='coerce')
    # Calculate ATR using finta
    atr = TA.ATR(ohlc)
    # print(atr)

    # Calculate take profit and stop loss prices
    takeprofitprice = decimal.Decimal(entry_price) + 1 * decimal.Decimal(atr[len(atr)-1])
    stoplossprice = decimal.Decimal(entry_price) - 1 * decimal.Decimal(atr[len(atr)-1])

    return takeprofitprice, stoplossprice


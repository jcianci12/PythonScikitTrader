import csv
import decimal
from finta import TA

import csv

import pandas as pd
from bybitapi import get_market_bid_price
from config import SYMBOL, TEST

from get_last_ohlc_bybit import get_last_ohlc_bybit

def save_updated_prices(filename, orders):
    # Write updated data to CSV file
    with open(filename, mode='w') as file:
        fieldnames = ['uid', 'symbol', 'side', 'qty', 'entryprice', 'takeprofitprice', 'stoplossprice', 'profit']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(orders)





from finta import TA

def calculate_prices(ohlc):
    if(ohlc==None):
        ohlc =get_last_ohlc_bybit(SYMBOL,"5") 
        ohlc = ohlc.apply(pd.to_numeric, errors='coerce')
    # else:
    entry_price = get_market_bid_price(TEST,SYMBOL)
        # Calculate ATR using finta

    atr = TA.ATR(ohlc)
        # print(atr)

    # Calculate take profit and stop loss prices
    tp,sl = get_tp_sl_from_ATR(atr,entry_price)
    tp=decimal.Decimal(tp)
    sl=decimal.Decimal(sl)

    return tp, sl

def get_tp_sl_from_ATR(atr,entry_price):
    entry_price = float(entry_price)
    # Calculate take profit and stop loss prices
    tp = float(entry_price) + 3 * (atr[len(atr)-1])
    sl = float(entry_price) - 2 * (atr[len(atr)-1])
    return tp,sl

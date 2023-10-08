import csv
import datetime
import decimal
import hashlib
import hmac
from logging import Logger
import time
import uuid
import pandas as pd
import requests
from KEYS import API_KEY, API_SECRET
from config import *
from functions.interval_map import *
from functions.logger import logger

from KEYS import API_KEY, API_SECRET
import ccxt


exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    "timeout":10000000
})
# very important set spot as default type
exchange.options['defaultType'] = 'spot'
exchange.load_markets()
DELAY = 5
TEST_URL = 'https://www.google.com'


def get_session(test=True):
    http = HTTP(testnet=False, api_key="...", api_secret="...")
    http.testnet = test
    http.endpoint = BASE_URL
    http.api_key = API_KEY
    http.api_secret = API_SECRET

    # Check for connection
    while True:
        try:
            requests.get(TEST_URL)
            break
        except requests.exceptions.RequestException:
            logger(f"Connection down... retrying in {DELAY} seconds")
            time.sleep(DELAY)

    return http


def get_min_qty_binance(symbol: str) -> float:
    markets = exchange.load_markets()
    market = markets[symbol]
    min_qty = market['limits']['amount']['min']
    return min_qty


def convert_interval_to_timespan(interval):
    minutes = interval_map[interval]
    return datetime.timedelta(minutes=minutes)


def get_intervals(start_date, end_date, interval):
    interval_timespan = convert_interval_to_timespan(interval)
    time_span_seconds = interval_timespan.total_seconds()
    total_seconds = (end_date - start_date).total_seconds()

    total_intervals = total_seconds // time_span_seconds
    print("there are ", datetime.timedelta(
        seconds=total_seconds).days, "total days in the range.")

    print(f'total_intervals: {total_intervals}')
    if total_intervals > 200:
        intervals = []
        for i in range(0, int(total_intervals), 200):
            intervals.append([i * time_span_seconds + start_date.timestamp(),
                             (i + 200) * time_span_seconds + start_date.timestamp()])
        print(f'intervals: {intervals}')
        return intervals
    else:
        intervals = [[start_date.timestamp(), end_date.timestamp()]]
        print(f'intervals: {intervals}')
        return intervals


def fetch_bybit_data_v5(test, start_date, end_date, symbol, interval, category):
    # Get the intervals for the given date range and interval
    intervals = get_intervals(start_date, end_date, interval)

    # Create an empty list to store the data
    data = []

    # Loop through each interval and make an API call for that interval
    for interval_start, interval_end in intervals:
        # Convert the start and end times to Unix timestamps in milliseconds
        start_ts = int(interval_start * 1000)
        end_ts = int(interval_end * 1000)

        print(
            f"Fetching historical data from {datetime.datetime.fromtimestamp(interval_start)} to {datetime.datetime.fromtimestamp(interval_end)}")

        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_ts,
            'endTime': end_ts,
        }

        try:
            response = exchange.fetch_ohlcv(symbol, interval, params=params)
            if response:
                data += response
            else:
                print(f"No data returned for this interval")
        except ccxt.BaseError as e:
            print("An error occurred while making the request:")
            print(e)
            print("Retrying after 1 minute...")
            time.sleep(60)  # Wait for 1 minute before retrying
            # Recursive call to retry fetching data
            return fetch_bybit_data_v5(exchange, start_date, end_date, symbol, interval)

# Convert the data to a DataFrame
    df_new = pd.DataFrame(data, columns=[
                        'open_time', 'open', 'high', 'low', 'close', 'volume'])
    df_new['timestamp'] = pd.to_datetime(df_new['open_time'], unit='ms')
    df_new.set_index('timestamp', inplace=True)
    df_new.sort_values(by=['open_time'], inplace=True)

    print("returning new")
    print(df_new)
    df_new.to_csv("new.csv")
    df_new = df_new[~df_new.index.duplicated(keep='first')]

    return df_new


# %%
# def get_wallet_balance(test, coin):

    
def get_free_balance(symbol: str) -> float:
        # Set up the exchange with your API key and secret
    

    # Fetch the balance for the specified symbol
    balance = exchange.fetch_balance()
    return balance[symbol]['free']
def get_value(symbol: str) -> float:
    # Fetch the balance for the specified symbol
    balance = exchange.fetch_balance()
    return balance[symbol]['free']


def get_market_bid_price(symbol: str) -> float:
    ticker = exchange.fetch_ticker(symbol)
    return float(ticker['bid'])



def get_market_ask_price(symbol: str) -> float:
    ticker = exchange.fetch_ticker(symbol)
    return float(exchange.price_to_precision(symbol,  ticker['ask']))


# get_market_ask_price(True, "BTCUSDT")
# %%
def place_order_tp_sl(testmode, type, symbol, side,usdtbalance,btcbalance, tp, sl, amount):
    logger(symbol, side, tp, sl, amount)
    try:
        # Get the market data
        exchange.load_markets()
        amount = exchange.amount_to_precision(symbol,amount)
        market = exchange.market(symbol)
        buyresponse = exchange.create_market_order(
            market['id'],side,
            amount
        )
        print(buyresponse)
      
        logger(buyresponse)
        fee = buyresponse['fees'][0]['cost']
        log_order(buyresponse,fee,symbol,side,usdtbalance,btcbalance,tp,sl)
   
        return buyresponse
    except Exception as e:
        logger(f"An error occurred while placing the order: {e}")
        return None

def log_order(buyresponse,fee,symbol,side,usdtbalance,btcbalance,tp,sl):
 # Save the order details to a CSV file
    with open('orders.csv', mode='a') as file:
        writer = csv.writer(file)

        # Write the header row if the file is empty
        if file.tell() == 0:
            writer.writerow(ORDERCOLUMNS)

        # Write the order details
        writer.writerow([
            buyresponse['clientOrderId'],
            datetime.datetime.now(),
            symbol,
            side,
            usdtbalance,
            btcbalance,
            usdtbalance + btcbalance*buyresponse['price'],
            buyresponse['filled']-fee,
            buyresponse['price'],
            tp,
            sl,
            "",
            "",
            ""
        ])
    
def cancel_order(symbol, id):
    try:
        exchange.cancel_order(id,TRADINGPAIR)

    except Exception as e:
        logger(f"An error occurred: {e}")




async def fetch_spot_balance(exchange):
    balance = await exchange.fetch_balance()
    print("Spot Balance:", balance)


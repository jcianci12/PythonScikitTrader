import csv
import datetime
import decimal
import hashlib
import hmac
from logging import Logger
import time
import uuid
import pandas as pd
from pybit.unified_trading import HTTP
import requests
from KEYS import API_KEY, API_SECRET
from config import *
from functions.interval_map import *
from functions.logger import logger

from KEYS import API_KEY, API_SECRET
import ccxt


exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})
# very important set spot as default type
exchange.options['defaultType'] = 'spot'

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
            'start': start_ts,
            'end': end_ts,
            'category': category,
        }

        if test:
            url = "https://api-testnet.bybit.com/v5/market/kline"
        else:
            url = "https://api.bybit.com/v5/market/kline"

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data += response.json()['result']['list']
            else:
                print(f"Error fetching data: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print("An error occurred while making the request:")
            print(e)
            print("Retrying after 1 minute...")
            time.sleep(60)  # Wait for 1 minute before retrying
            # Recursive call to retry fetching data
            return fetch_bybit_data_v5(test, start_date, end_date, symbol, interval, category)

    # Convert the data to a DataFrame
    df_new = pd.DataFrame(data, columns=[
                          'open_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
    df_new['timestamp'] = pd.to_datetime(df_new['open_time'], unit='ms')
    df_new.set_index('timestamp', inplace=True)
    df_new.sort_values(by=['open_time'], inplace=True)

    print("returning new")
    print(df_new)
    df_new.to_csv("new.csv")
    df_new = df_new[~df_new.index.duplicated(keep='first')]

    return df_new


# %%
def get_wallet_balance(test, coin):

    print("fetching balance on coin ", coin)
    http = get_session(test)

    response = http.get_wallet_balance(accountType=ACCOUNT_TYPE, coin=coin,)
    coins = response["result"]["list"][0]["coin"]

    for c in coins:
        if c["coin"] == coin:
            wallet_balance = c["availableToWithdraw"]
            print("current wallet balance available is:", wallet_balance)
            return str(wallet_balance)
    print(f"No wallet balance found for coin: {coin}")
    return "0"

# %%


def get_market_bid_price(test, symbol):
    from pybit.unified_trading import HTTP

    response = get_session().get_tickers(
        category="spot",
        symbol=symbol,
    )

    if response['retCode'] == 0:
        data = response['result']['list']
        bid_price = data[0]['bid1Price']
        print(f"Current bid price for {symbol}: {bid_price}")
        return str(bid_price)
    else:
        print("Error:", response['retMsg'])
        return str()


def get_market_ask_price(test, symbol):
    from pybit.unified_trading import HTTP

    response = get_session().get_tickers(
        category="spot",
        symbol=symbol,
    )

    if response['retCode'] == 0:
        data = response['result']['list']
        ask_price = data[0]['ask1Price']
        print(f"Current ask price for {symbol}: {ask_price}")
        return str(ask_price)
    else:
        print("Error:", response['retMsg'])
        return str()


# get_market_ask_price(True, "BTCUSDT")
# %%

def place_order(testmode, type, symbol, side, tp, sl, qty):
    try:
        # Get the market data
        market_data = get_market_ask_price(testmode, symbol="BTCUSDT")

        # Get the market price
        market_price = float(market_data)
        btcqty = float(qty)/market_price
        tp = round(tp, 2)
        sl = round(sl, 2)

        exchange = ccxt.bybit({
            'apiKey': API_KEY,
            'secret': API_SECRET,
        })
        exchange.options['defaultType'] = 'spot'
        # exchange.verbose = True


        # # Python
        symbol = 'BTC/USDT'
        type = 'market'  # or 'market'
        side = 'buy'
        amount = btcqty  # your amount
        price = market_price  # your price
        stopLossTriggerPrice = sl
        TakeProfitTriggerPrice = tp
        tpparams = {
            'triggerPrice': TakeProfitTriggerPrice,  # your stop price
        }
        slparams = {
            'triggerPrice': stopLossTriggerPrice,  # your stop price
        }

        initial_order = exchange.create_order(symbol, "market", side, amount, price)
        stop_loss_order = exchange.create_order (symbol, "limit", "sell", amount, price, slparams)
        take_profit_order = exchange.create_order (symbol, "limit", "sell", amount, price, tpparams)

# Save the order details to a CSV file
        with open('orders.csv', mode='a') as file:
            writer = csv.writer(file)

            # Write the header row if the file is empty
            if file.tell() == 0:
                writer.writerow(ORDERCOLUMNS)

            # Write the order details
            writer.writerow([
                initial_order['id'],
                datetime.datetime.now(),
                symbol,
                side,
                qty,
                market_price,
                tp,
                sl,
                take_profit_order['id'],
                stop_loss_order['id'],
                ""
            ])
            return initial_order
    except Exception as e:
        logger(f"An error occurred: {e}")
    return None


def cancel_order(symbol, id):
    try:
        get_session(TEST).cancel_order(
            category="spot",
            symbol=symbol,
            orderId=id
        )
    except Exception as e:
        logger(f"An error occurred: {e}")


# print(Test_Buy_and_Sell())
# %%
def cancel_all(test, coin):
    session = get_session(test)
    response = session.cancel_all_orders(category="spot", settleCoin=coin)
    return response


def get_server_time():
    response = requests.get('https://api.bybit.com/v2/public/time')
    data = response.json()
    server_time = data['time_now']
    logger("server time is:", server_time)
    return server_time


def load_time_difference(self, params={}):
    serverTime = self.fetch_time(params)
    after = self.milliseconds()
    self.options['timeDifference'] = after - serverTime
    return self.options['timeDifference']


def fetch_time(self, params={}):
    response = self.publicGetTime(params)
    return self.safe_timestamp(response, 'time_now')


async def fetch_spot_balance(exchange):
    balance = await exchange.fetch_balance()
    print("Spot Balance:", balance)


async def create_limit_order(exchange, symbol, order_type, side, amount, price):
    create_order = await exchange.create_order(symbol, order_type, side, amount, price)
    print('Created Order ID:', create_order['id'])


# async def cancel_order(exchange, order_id, symbol):
#     canceled_order = await exchange.cancel_order(order_id, symbol)
#     print('Canceled Order ID:', canceled_order['id'])


async def fetch_closed_orders(exchange, symbol):
    orders = await exchange.fetch_closed_orders(symbol)
    print("Canceled Orders:", orders)

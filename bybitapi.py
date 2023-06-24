import datetime
import decimal
import uuid
import pandas as pd
from pybit.unified_trading import HTTP
import requests
from KEYS import API_KEY, API_SECRET, TESTNET_API_KEY, TESTNET_API_SECRET
from config import *
from interval_map import *


def get_session(test=True):
    http = HTTP(testnet=False, api_key="...", api_secret="...")
    http.testnet = test
    http.endpoint = TESTNET_BASE_URL if test else BASE_URL
    http.api_key = TESTNET_API_KEY if test else API_KEY
    http.api_secret = TESTNET_API_SECRET if test else API_SECRET
    return http

def convert_interval_to_timespan(interval):
    minutes = interval_map[interval]
    return datetime.timedelta(minutes=minutes)

def get_intervals(start_date, end_date, interval):
    interval_timespan = convert_interval_to_timespan(interval)
    time_span_seconds = interval_timespan.total_seconds()
    total_seconds = (end_date - start_date).total_seconds()

    total_intervals = total_seconds // time_span_seconds
    print ("there are " ,datetime.timedelta(seconds=total_seconds).days,"total days in the range.")
    
    print(f'total_intervals: {total_intervals}')
    if total_intervals > 200:
        intervals = []
        for i in range(0, int(total_intervals), 200):
            intervals.append([i * time_span_seconds + start_date.timestamp(), (i + 200) * time_span_seconds + start_date.timestamp()])
        print(f'intervals: {intervals}')
        return intervals
    else:
        intervals = [[start_date.timestamp(), end_date.timestamp()]]
        print(f'intervals: {intervals}')
        return intervals

def fetch_bybit_data_v5(test,start_date, end_date, symbol, interval, category):
    # Get the intervals for the given date range and interval
    intervals = get_intervals(start_date, end_date, interval)

    # Create an empty list to store the data
    data = []

    # Loop through each interval and make an API call for that interval
    for interval_start, interval_end in intervals:
        # Convert the start and end times to Unix timestamps in milliseconds
        start_ts = int(interval_start * 1000)
        end_ts = int(interval_end * 1000)

        print(f"Fetching historical data from {datetime.datetime.fromtimestamp(interval_start)} to {datetime.datetime.fromtimestamp(interval_end)}")

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

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data += response.json()['result']['list']
        else:
            print(f"Error fetching data: {response.status_code}")

    # Convert the data to a DataFrame
    df_new = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
    df_new['timestamp'] = pd.to_datetime(df_new['open_time'].astype(str), unit='ms')
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

    response = http.get_wallet_balance(accountType="SPOT", coin=coin)
    coins = response["result"]["list"][0]["coin"]

    for c in coins:
        if c["coin"] == coin:
            wallet_balance = c["walletBalance"]
            print("current wallet balance is:" ,wallet_balance)
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

import pybit


def place_buy_order(
    testmode, symbol,walletcoin, take_profit_percent, stop_loss_percent, capitalpercent
):
    session = get_session(testmode)
    # Get the market data
    market_data = get_market_ask_price(testmode, symbol=symbol)
    # Get the market price
    market_price = float(market_data)
    # Get the capital
    capital = float(get_wallet_balance(testmode, walletcoin))
    # min =a if a < b else b
    take_profit_price =  None if take_profit_percent ==None else  (market_price * (1 + take_profit_percent / 100))
    stop_loss_price =None if stop_loss_percent ==None else   (market_price * (1 - stop_loss_percent / 100))
    # note this is the amount of money we want to spend!
    qty = capital * (capitalpercent / 100)
    qtyf = format(qty, ".5f")
    print("placing buy order of ",symbol, "qty:" ,qty)
    response = session.place_order(
        category="spot",
        symbol=symbol,
        side="Buy",
        orderType="Market",
        qty=qtyf,
        timeInForce="GTC",
        takeProfit=take_profit_price,
        stopLoss=stop_loss_price,
        orderLinkId=str(uuid.uuid4()),
    )
    return response


def place_sell_order(testmode, capitalsymbol, marketsymbol, capitalpercent):
    session = get_session(testmode)
    # Get the market data
    market_data = get_market_bid_price(testmode, symbol=marketsymbol)
    # Get the market price
    balance = decimal.Decimal(get_wallet_balance(testmode,capitalsymbol))
    # value = decimal.Decimal(get_market_bid_price(testmode,marketsymbol))
      # note this is the amount of money we want to spend!
    qty = ( decimal.Decimal(capitalpercent) / 100)*balance
    qty_rounded = qty.quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)

    # qtyf = format(qty,".5f" )
    response = session.place_order(
        category="spot",
        symbol=marketsymbol,
        side="Sell",
        orderType="Market",
        qty=str(qty_rounded),
        timeInForce="GTC",
        orderLinkId=str(uuid.uuid4()),
    )
    
    return response


# %%
def Test_Buy_and_Sell():
    # place order using 2 percent of capital
    buy = place_buy_order(True, "BTCUSDT","USDT", 5, 5, 2)
    # sell 100% of the coin just purchased
    sell = place_sell_order(True, "BTC", "BTCUSDT", 100)
    return sell, buy


def fetch_bybit_current_orders():
    from pybit.unified_trading import HTTP
    import pandas as pd

    

    response = get_session().get_open_orders(
        category="spot",
        symbol="BTCUSDT",
        openOnly=0,
        limit=20,
    )

    if response['retCode'] == 0:
        data = response['result']['list']
        df_new = pd.DataFrame(data)

        # Filter by outstanding orders
        df_new = df_new[df_new['orderStatus'] == 'New']

        print("returning",df_new)
        return df_new
    else:
        print("Error:", response['retMsg'])
    


# print(Test_Buy_and_Sell())
# %%
def cancel_all(test, coin):
    session = get_session(test)
    response = session.cancel_all_orders(category="spot", settleCoin=coin)
    return response

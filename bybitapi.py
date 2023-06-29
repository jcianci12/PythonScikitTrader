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
            wallet_balance = c["walletBalance"]
            print("current wallet balance is:" ,wallet_balance)
            return str(wallet_balance)
    print(f"No wallet balance found for coin: {coin}")
    return "0"



def get_wallet_balance_new(test, coin):
    print(f"fetching balance on coin {coin}")

    api_key = API_KEY
    secret = API_SECRET

    timestamp = int(time.time() * 1000)
    recv_window = 20000

    query_string = f'coin={coin}&timestamp={timestamp}&recv_window={recv_window}'
    signature = hmac.new(bytes(secret, 'utf-8'), bytes(query_string, 'utf-8'), hashlib.sha256).hexdigest()

    url = f'https://api-testnet.bybit.com/v5/account/wallet-balance?{query_string}&sign={signature}'

    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-TIMESTAMP': str(timestamp),
        'X-BAPI-RECV-WINDOW': str(recv_window),
        'X-BAPI-SIGN': signature
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    coins = data['result'][coin]

    wallet_balance = coins['wallet_balance']
    print(f"current wallet balance is: {wallet_balance}")
    return str(wallet_balance)



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

def place_buy_order(testmode, symbol, capitalsymbol, take_profit_percent, stop_loss_percent, qty):
    """
    Function to place a buy order.
    :param testmode: Boolean indicating if test mode is enabled.
    :param symbol: The symbol for the market asset.
    :param capitalsymbol: The symbol for the capital asset.
    :param take_profit_percent: The take profit percentage for the order.
    :param stop_loss_percent: The stop loss percentage for the order.
    :param qty: The quantity to buy.
    """
    try:
        session = get_session(testmode)
        
        # Get the market data
        market_data = get_market_ask_price(testmode, symbol=symbol)
        
        # Get the market price
        market_price = float(market_data)
        
        # Calculate the take profit and stop loss prices
        take_profit_price = None if take_profit_percent == None else (market_price * (1 + take_profit_percent / 100))
        stop_loss_price = None if stop_loss_percent == None else (market_price * (1 - stop_loss_percent / 100))
        
        print("placing buy order of ", symbol, "qty:", qty)
        
        response = session.place_order(
            category="spot",
            symbol=symbol,
            side="Buy",
            orderType="Market",
            qty=str(qty),
            timeInForce="GTC",
            takeProfit=take_profit_price,
            stopLoss=stop_loss_price,
            orderLinkId=str(uuid.uuid4()),
        )
    except Exception as e:
        logger(f"the error: {e}")
        raise e

    return response


def place_sell_order(testmode, capitalsymbol, marketsymbol, qty):
    """
    Function to place a sell order.
    :param testmode: Boolean indicating if test mode is enabled.
    :param capitalsymbol: The symbol for the capital asset.
    :param marketsymbol: The symbol for the market asset.
    :param qty: The quantity to sell.
    """
    try:
        session = get_session(testmode)
        
        response = session.place_order(
            category="spot",
            symbol=marketsymbol,
            side="Sell",
            orderType="Market",
            qty=str(qty),
            timeInForce="GTC",
            orderLinkId=str(uuid.uuid4()),
        )
    except Exception as e:
        Logger(f"the error: {e}")
        raise e

    return response



def Test_Buy_and_Sell():
    """
    Function to test buying and selling.
    """
    # Get the USDT balance
    usdtbalance = decimal.Decimal(get_wallet_balance(True, "USDT"))
    
    # Calculate the quantity to buy (2% of USDT balance)
    qty = (2 / 100) * usdtbalance
    qty_rounded = qty.quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)
    
    # Check if qty_rounded is less than the minimum order quantity
    min_qty = decimal.Decimal('0.000001')
    if qty_rounded < min_qty:
        logger(f"Sale of {qty_rounded} was below minimum amount.")
        qty_rounded = min_qty
    
    # Place a buy order using 2% of USDT balance
    buy = place_buy_order(True, "BTCUSDT", "USDT", 5, 5, qty_rounded)
    
    # Get the BTC balance
    btcbalance = decimal.Decimal(get_wallet_balance(True, "BTC"))
    
    # Place a sell order for 100% of the BTC balance
    sell = place_sell_order(True, "BTC", "BTCUSDT", btcbalance)
    
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

def get_server_time():
    response = requests.get('https://api.bybit.com/v2/public/time')
    data = response.json()
    server_time = data['time_now']
    logger("server time is:" ,server_time)
    return server_time

def load_time_difference(self, params={}):
    serverTime = self.fetch_time(params)
    after = self.milliseconds()
    self.options['timeDifference'] = after - serverTime
    return self.options['timeDifference']

    def fetch_time(self, params={}):
        response = self.publicGetTime(params) 
        return self.safe_timestamp(response, 'time_now')

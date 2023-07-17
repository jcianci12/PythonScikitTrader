import requests
import pandas as pd

def get_last_ohlc_bybit( symbol, timeframe):
    category = 'spot'
    # Set API endpoint and parameters
    url = 'https://api.bybit.com/v5/market/kline'
    params = {
        'category': category,
        'symbol': symbol,
        'interval': timeframe,
        'limit': 20
    }

    # Send API request
    response = requests.get(url, params=params)
    data = response.json()

    # Convert data to DataFrame
    df = pd.DataFrame(data['result']['list'], columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
    # df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    # df = df.set_index('open_time')

    return df


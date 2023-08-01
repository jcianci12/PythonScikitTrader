import ccxt

def get_latest_price(symbol: str) -> float:
    exchange = ccxt.binance()
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']


price = get_latest_price('BTC/USDT')
print(f"The latest price of BTC/USDT is {price}")



from bybitapi import exchange

def convert_to_usdt(symbol:str,amount:float)->float:
    #get the latest price using the ccxt api. The exchange is binance
    ticker = exchange.fetch_ticker(symbol)
    latestprice = ticker['last']

    value = latestprice * amount
    return value

def get_balance() -> float:
    # Set up the exchange with your API key and secret
  

    # Fetch the balance for the specified symbol
    balance = exchange.fetch_balance()

    # Initialize a variable to store the total balance amount
    total_balance = 0
    # Loop through the balances list in the info dictionary
    for coin in balance['info']['balances']:
    # Convert the free and locked amounts to floats and add them to the total balance
        coinbalance = float(coin['free']) + float(coin['locked'])
        if(coinbalance>0 and coin['asset']!='USDT'):
            coinbalance = convert_to_usdt(coin['asset']+"/USDT",coinbalance)
        total_balance+=coinbalance


    # Print the total balance amount
    return total_balance

# Example usage
symbol = 'BTC'
balance = get_balance()
print(f'Your balance for {symbol} is: {balance}')
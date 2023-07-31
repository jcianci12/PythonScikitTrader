from bybitapi import exchange


def get_balance(symbol: str) -> float:
    # Set up the exchange with your API key and secret
  

    # Fetch the balance for the specified symbol
    balance = exchange.fetch_balance()
    return balance[symbol]['free']

# Example usage
symbol = 'BTC'
balance = get_balance(symbol)
print(f'Your balance for {symbol} is: {balance}')
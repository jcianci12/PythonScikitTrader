import asyncio
from  bybitapi import exchange

# Python
exchange.load_markets()
symbol = 'BTC/USDT'


def fetch_spot_balance(exchange):
    balance = exchange.fetch_balance()
    print("Spot Balance:", balance)

fetch_spot_balance(exchange)
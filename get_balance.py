import asyncio
from bybitapi import exchange

# Python
exchange.load_markets()
symbol = 'BTC/USDT'


def fetch_spot_balance(exchange):
    params = {"accountType": "UNIFIED",
              "coin": "BTC"}
    balance = exchange.private(params)
    print("Spot Balance:", balance)


fetch_spot_balance(exchange)

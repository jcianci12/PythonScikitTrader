import asyncio
import ccxt.async_support as ccxt

from KEYS import API_KEY, API_SECRET

exchange = ccxt.bybit({
            'apiKey': API_KEY,
            'secret': API_SECRET,
        })
exchange.options['defaultType'] = 'spot'

if exchange.has['fetchOrder']:
    order = asyncio.run(exchange.fetchClosedOrders())
    print(order)
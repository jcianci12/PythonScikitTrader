import ccxt

from KEYS import API_KEY, API_SECRET

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
amount = 0.001  # your amount
price = 30000  # your price
stopLossTriggerPrice = 28500
TakeProfitTriggerPrice = 31000
tpparams = {
    'triggerPrice': TakeProfitTriggerPrice,  # your stop price
}
slparams = {
    'triggerPrice': stopLossTriggerPrice,  # your stop price
}

order = exchange.create_order(symbol, "market", side, amount, price)
slorder = exchange.create_order (symbol, "limit", "sell", amount, price, slparams)
slorder = exchange.create_order (symbol, "limit", "sell", amount, price, tpparams)
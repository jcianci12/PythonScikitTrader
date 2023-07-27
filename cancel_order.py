from bybitapi import exchange

allorders = exchange.fetch_closed_orders()
canceled_orders = exchange.fetch_canceled_orders()
closed_orders = allorders+canceled_orders    # open_orders = exchange.fetch_open_orders()
open_orders = exchange.fetch_open_orders()
allorders =allorders+open_orders

print("closed orders:")
for number in closed_orders:
            print(number['info']['orderId'])


exchange.cancel_order("1473690407914266880","BTC/USDT")

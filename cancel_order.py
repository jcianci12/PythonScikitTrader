from bybitapi import exchange

allorders = exchange.fetchClosedOrders()
canceled_orders = exchange.fetch_canceled_orders()
closed_orders = allorders+canceled_orders    # open_orders = exchange.fetch_open_orders()
open_orders = exchange.fetch_open_orders()
allorders =allorders+open_orders

print("closed orders:")
for number in closed_orders:
            print(number['info']['orderId'])


exchange.cancel_order("78644992","BTC/USDT")

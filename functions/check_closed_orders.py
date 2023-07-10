import csv

from bybitapi import fetch_closed_orders

def check_closed_orders():
    with open('orders.csv', mode='r') as orders_file:
        reader = csv.DictReader(orders_file)
        rows = list(reader)

    for row in rows:
        if row['tp_order_id'] and row['sl_order_id']:
            tp_order = fetch_closed_orders(symbol=row['symbol'], orderId=row['tp_order_id'])
            sl_order = fetch_closed_orders(symbol=row['symbol'], orderId=row['sl_order_id'])

            if tp_order['status'] == 'FILLED' and sl_order['status'] == 'FILLED':
                profit = (float(tp_order['price']) - float(row['price'])) * float(row['quantity'])
                row['profit'] = profit
                row['status'] = 'COMPLETE'

    with open('orders.csv', mode='w') as orders_file:
        fieldnames = ['order_id', 'symbol', 'side', 'type', 'quantity', 'price', 'tp_order_id', 'sl_order_id', 'profit', 'status']
        writer = csv.DictWriter(orders_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)

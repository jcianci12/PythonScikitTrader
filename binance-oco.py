import csv
import datetime
from api import exchange, get_market_ask_price
from config import ORDERCOLUMNS, TEST
from functions.logger import logger
from generateTPandSL import calculate_prices

def place_order(testmode, type, symbol, side, tp, sl, amount):
    try:
        # Get the market data
        market_data = get_market_ask_price(symbol)

        # Get the market price
        market_price = float(market_data)

        type = 'limit'  # or 'market'
        side = 'buy'
        price = market_price  # your price
        exchange.load_markets()

        market = exchange.market(symbol)
        
        # Initialize a flag for the order status
        order_filled = False
        
        # Loop until the order is filled or a maximum number of attempts is reached
        max_attempts = 10
        attempts = 0
        
        while not order_filled:
            # Try to create a market buy order
            buyresponse = exchange.create_market_buy_order(
                market['id'],
                amount
            )
            print(buyresponse)
            
            # Check the status of the order
            if buyresponse['status'] == 'filled':
                # The order is filled, set the flag to True and break the loop
                order_filled = True
                break
            else:
                # The order is not filled, increment the price by 0.01 and try again
                price += 0.01
                attempts += 1
        
        # If the order is filled, create an oco order for sell
        if order_filled:
            ocoresponse = exchange.private_post_order_oco({
                'symbol': market['id'],
                'side': 'SELL',  # SELL, BUY
                'quantity': exchange.amount_to_precision(symbol, amount),
                'price': exchange.price_to_precision(symbol, price),
                'stopPrice': exchange.price_to_precision(symbol, sl),
                'stopLimitPrice': exchange.price_to_precision(symbol, tp),  # If provided, stopLimitTimeInForce is required
                'stopLimitTimeInForce': 'GTC',  # GTC, FOK, IOC
            })
            logger(ocoresponse)
            
            # Save the order details to a CSV file
            with open('orders.csv', mode='a') as file:
                writer = csv.writer(file)

                # Write the header row if the file is empty
                if file.tell() == 0:
                    writer.writerow(ORDERCOLUMNS)

                # Write the order details
                writer.writerow([
                    ocoresponse['listClientOrderId'],
                    datetime.datetime.now(),
                    symbol,
                    side,
                    amount,
                    market_price,
                    tp,
                    sl,
                    ocoresponse['orders'][0]['clientOrderId'],
                    ocoresponse['orders'][1]['clientOrderId'],
                    ""
                ])
                return ocoresponse
    except Exception as e:
        logger(f"An error occurred while placing an order: {e}")

    
tp,sl = calculate_prices(None)
place_order(TEST,"","BTC/USDT","BUY",tp,sl,0.0004)
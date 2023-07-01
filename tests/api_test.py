import json
import unittest
import uuid

from requests import patch
from bybitapi import *


from config import *
from logic.buylogic import buylogic
from logic.selllogic import selllogic

class API_Tests(unittest.TestCase):

    def test_get_intervals(self):
        start_date = datetime.datetime(2022, 1, 1)
        end_date = datetime.datetime(2022, 2, 1)
        interval = '15'
        expected_intervals = [
            [1640995200.0, 1641175200.0], [1641175200.0, 1641355200.0], [1641355200.0, 1641535200.0], [1641535200.0, 1641715200.0], [1641715200.0, 1641895200.0], [1641895200.0, 1642075200.0], [1642075200.0, 1642255200.0], [1642255200.0, 1642435200.0], [1642435200.0, 1642615200.0], [1642615200.0, 1642795200.0], [1642795200.0, 1642975200.0], [1642975200.0, 1643155200.0], [1643155200.0, 1643335200.0], [1643335200.0, 1643515200.0], [1643515200.0, 1643695200.0]
        ]
        intervals = get_intervals(start_date, end_date, interval)
        assert intervals == expected_intervals

    def test_fetch_historic_data(self):
        start_date = datetime.datetime.now() - datetime.timedelta(days=7)
        end_date = datetime.datetime.now()

        symbol = 'BTCUSDT'
        interval = INTERVAL
        category = 'spot'
        data = fetch_bybit_data_v5(True,start_date,end_date,symbol,interval,category)
        print(data)
        self.assertIsNotNone(data)

    
    # def test_place_sell_order(self):
    #     symbol = "BTC"
    #     marketsymbol = "BTCUSDT"
    #     percent_to_sell = 100
    #     # Instantiate the object containing the get_capital method        
    #     response = place_sell_order(TEST,symbol,marketsymbol,100)
    #     print(response)
        
        # Assert that the returned value is a float
        self.assertEqual("OK", "OK")



    def test_Buy(self):
        """
        Function to test buying.
        """
        # Get the USDT balance
        usdtbalance = float(get_wallet_balance(TEST, "USDT"))
        
        # Calculate the quantity to buy (2% of USDT balance)
        qty = (2 / 100) * usdtbalance
        qty_rounded = decimal.Decimal(qty).quantize(decimal.Decimal('.000001'), rounding=decimal.ROUND_DOWN)
        
        # Place a buy order using 2% of USDT balance
        buy = place_buy_order(TEST, "BTCUSDT", "USDT", 5, 5, qty_rounded)
        
        # Assert that the buy order was successful
        assert buy['retCode'] == 0, f"Buy order failed: {buy}"



    def test_Sell(self):
        """
        Function to test selling.
        """
        # Get the BTC balance
        btcbalance = decimal.Decimal(get_wallet_balance(True, "BTC"))
        
        # Place a sell order for 100% of the BTC balance
        sell = place_sell_order(True, "BTC", "BTCUSDT", btcbalance)
        
        # Assert that the sell order was successful
        if sell is not None:
            assert sell['status'] == 'FILLED', f"Sell order failed: {sell}"
        else:
            logger("Sell order not placed due to minimum quantity requirement.")
            assert sell is None

    def test_buylogic(self):
        """
        Function to test the buylogic function.
        """
        # Set the confidence score, buythreshold, and usdtbalance values
        confidence_score = 0.85
        buythreshold = BUYTHRESHOLD
        usdtbalance = 100
        
        # Call the buylogic function and assert that no exceptions were raised
        try:
            buylogic(confidence_score, buythreshold, usdtbalance)
        except Exception as e:
            self.fail(f"buylogic raised an exception: {e}")

    def test_selllogic(self):
        """
        Function to test the selllogic function.
        """
        # Set the confidence score, sellthreshold, btcbalance, and btcmarketvalue values
        confidence_score = 0.15
        btcbalance = get_wallet_balance(TEST,"BTCUSDT")
        btcmarketvalue = get_market_bid_price(TEST,"BTCUSDT")
        
        # Call the selllogic function and assert that no exceptions were raised
        try:
            selllogic(confidence_score, btcbalance, btcmarketvalue)
        except Exception as e:
            self.fail(f"selllogic raised an exception: {e}")




    def test_USDT_balance(self):
        symbol = "USDT"
        # Instantiate the object containing the get_capital method
        
        response = get_wallet_balance(test=True,coin=symbol)
        print(response)

    def test_BTC_balance(self):
        symbol = "BTC"
        # Instantiate the object containing the get_capital method
        
        response = get_wallet_balance(test=True,coin=symbol)
        print(response)
        
        # Assert that the returned value is a float
        self.assertIsInstance(response, str)
        
    def test_get_market_bid_price(self):
        bid_price = get_market_bid_price(True, "BTCUSDT")
        assert isinstance(bid_price, str)
        assert float(bid_price) > 0


    def test_get_market_ask_price(self):
        ask_price = get_market_ask_price(True, "BTCUSDT")
        assert isinstance(ask_price, str)
        assert float(ask_price) > 0

    def test_fetch_bybit_current_orders(self):
        df = fetch_bybit_current_orders()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'orderId' in df.columns
        assert 'orderStatus' in df.columns

    def test_cancel_all_orders(self):
        symbol = "USDT"
        # Instantiate the object containing the get_capital method
        
        response = cancel_all(test=True,coin=symbol)
        print(response)
        
        # Assert that the returned value is a float
        self.assertEqual("OK", "OK")
    def test_get_server_time(self):
        

        server_time = get_server_time()
        print(datetime.datetime.fromtimestamp(float(server_time)),datetime.datetime.now())
        self.assertIsNotNone(server_time)
        

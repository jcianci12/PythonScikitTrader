import datetime
import decimal
import time
import unittest
import pandas as pd



from bybitapi import  fetch_bybit_data_v5, get_intervals, get_market_ask_price, get_market_bid_price,  get_free_balance,  place_order_tp_sl
from config import BUYTHRESHOLD, INTERVAL, TEST
from logic.buylogic import buylogic
from logic.selllogic import selllogic
from messengerservice import send_telegram_message
import unittest
import asyncio



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
    


    # def test_Buy(self):
    #     """
    #     Function to test buying.
    #     """
    #     # Get the USDT balance
        

    #     # Calculate the quantity to buy (2% of USDT balance)
               
    #     tp,sl = calculate_prices(None)
    #     # Place a buy order using 2% of USDT balance
    #     buy = place_order_tp_sl(TEST,"market", "BTCUSDT","buy",tp,sl,  0.0004)
        
    #     # Assert that the buy order was successful
    #     assert True


    # def test_sell(self):
    #     """
    #     Function to test buying.
    #     """
    #     # Get the USDT balance
        

    #     # Calculate the quantity to buy (2% of USDT balance)
               
    #     tp,sl = calculate_prices(None)
    #     # Place a buy order using 2% of USDT balance
    #     buy = place_order_tp_sl(TEST,"market", "BTCUSDT","sell",tp,sl,  0.0004)
        
    #     # Assert that the buy order was successful
    #     assert buy['retCode'] == 0, f"Buy order failed: {buy}"  

    def test_buylogic(self):
        """
        Function to test the buylogic function.
        """
        # Set the confidence score, buythreshold, and usdtbalance values
        confidence_score = 1
        buythreshold = BUYTHRESHOLD
        usdtbalance = get_free_balance("USDT")
        
        # Call the buylogic function and assert that no exceptions were raised
        try:
            buylogic(confidence_score,  usdtbalance)
        except Exception as e:
            self.fail(f"buylogic raised an exception: {e}")

    def test_selllogic(self):
        """
        Function to test the selllogic function.
        """
        # Set the confidence score, sellthreshold, btcbalance, and btcmarketvalue values
        confidence_score = 0.15
        btcbalance = get_free_balance(TEST,"BTCUSDT")
        btcmarketvalue = get_market_bid_price(TEST,"BTCUSDT")
        
        # Call the selllogic function and assert that no exceptions were raised
        try:
            selllogic(confidence_score, btcbalance, btcmarketvalue)
        except Exception as e:
            self.fail(f"selllogic raised an exception: {e}")
    # def test_checkorders(self):
    #     check_orders()

    def test_send_message(self):
        asyncio.run(send_telegram_message('Your message here'))


    def test_USDT_balance(self):
        symbol = "USDT"
        # Instantiate the object containing the get_capital method
        
        response = get_free_balance(test=True,coin=symbol)
        print(response)

    def test_BTC_balance(self):
        symbol = "BTC"
        # Instantiate the object containing the get_capital method
        
        response = get_free_balance(test=True,coin=symbol)
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






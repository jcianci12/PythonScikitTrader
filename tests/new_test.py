import unittest
from unittest.mock import patch, Mock

from ..api import fetch_candle_data, place_order_tp_sl
from config import INTERVAL, TEST
from get_tp_sl import get_tp_sl
from prep_data import prep_data

class TestPlaceOrder(unittest.TestCase):
    @patch('your_module.logger')
    @patch('your_module.exchange')
    
    def test_place_order_tp_sl(self, mock_exchange, mock_logger):
            # fetch the kline (historical data)
        category = 'spot'

        data = fetch_candle_data(
            TEST, "2024/", "end_date", "BTCUSDT", INTERVAL, category)
        # data = old_fetch_bybit_data_v5(True,start_date,end_date,"BTCUSDT",interval,category)
        # smooth the data
        data = prep_data(data)
        # Arrange
        tp,sl = get_tp_sl(data,len(data)-1)

        mock_exchange.load_markets.side_effect = Exception('Test Exception')
        testmode = 'test'
        type = 'market'
        symbol = 'BTCUSDT'
        side = 'buy'
        usdtbalance = 100
        btcbalance = 0
        tp = 1
        sl = 1
        amount = 1

        # Act
        result = place_order_tp_sl(testmode, type, symbol, side, usdtbalance, btcbalance, tp, sl, amount)

        # Assert
        self.assertIsNone(result)
        mock_logger.assert_called_with('An error occurred while placing the order: Test Exception')

if __name__ == '__main__':
    unittest.main()

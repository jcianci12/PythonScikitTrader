from pybit.unified_trading import WebSocket
from time import sleep
ws = WebSocket(
    testnet=True,
    channel_type="spot",
)
def handle_message(message):
    if 'topic' in message and message['topic'] == 'tickers.BTCUSDT':
        last_price = message['data']['lastPrice']
        print(last_price)

ws.ticker_stream(
    symbol="BTCUSDT",
    callback=handle_message
)
while True:
    sleep(1)

import decimal


TEST=False

BASE_URL = "https://api-testnet.bybit.com" if TEST else "https://api.bybit.com"

WEBSOCKET_BASE_URL = "wss://stream.bybit.com/realtime"

ACCOUNT_TYPE = "SPOT" if TEST else "UNIFIED"

SYMBOL = "BTCUSDT"

MAXBUYPERCENTOFCAPITAL = 10
MAXSELLPERCENTOFCAPITAL = 10

MINIMUMBTCTRANSACTIONSIZE = 0.000048

TAKEPROFIT = 3
STOPLOSS = 1.5

BUYTHRESHOLD = 0.8
SELLTHRESHOLD = 0.4

DATALENGTHFORTRAININGINDAYS = 3
DATALENGTHFORTRADINGINDAYS = 1

INTERVAL = '5m'

ALWAYSRETRAIN = False
TESTRETRAINATSTART = False


PERCENTCHANGEINDICATOR = 0.005
LOOKAHEADVALUE = 15

PLOTBACKTEST = False
PLOTPROGRESS = True
SIMULATETRADE = False

GRAPHVIEWWINDOW = 30
ALLOWEDTOSELL = False

ORDERCOLUMNS = ['uid', 'date','symbol', 'side', 'qty', 'entryprice', 'takeprofitprice', 'stoplossprice', 'takeprofitid', 'stoplossid', 'profit', 'completedtime']

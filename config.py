
import decimal


TEST=False

BASE_URL = "https://api-testnet.bybit.com" if TEST else "https://api.bybit.com"

WEBSOCKET_BASE_URL = "wss://stream.bybit.com/realtime"

ACCOUNT_TYPE = "SPOT" if TEST else "UNIFIED"





MAXBUYPERCENTOFCAPITAL = decimal.Decimal(50)
MAXSELLPERCENTOFCAPITAL = decimal.Decimal(50)

MINIMUMBTCTRANSACTIONSIZE = decimal.Decimal(0.000048)

TAKEPROFIT = decimal.Decimal(4 /100) #4 percent
STOPLOSS = decimal.Decimal(2/100)

BUYTHRESHOLD = 0.8
SELLTHRESHOLD = 0.4

DATALENGTHFORTRAININGINDAYS = 5
DATALENGTHFORTRADINGINDAYS = 1

INTERVAL = '5'

ALWAYSRETRAIN = False
TESTRETRAINATSTART = False


PERCENTCHANGEINDICATOR = 0.005
LOOKAHEADVALUE = 15

PLOTBACKTEST = False
PLOTPROGRESS = True
SIMULATETRADE = False

GRAPHVIEWWINDOW = 96
ALLOWEDTOSELL = False



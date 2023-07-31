import hashlib
import hmac
import time
import uuid

import requests
from KEYS import API_KEY, API_SECRET
from bybitapi import exchange, get_session
from config import BASE_URL, TEST

# params ={
# 	"symbol_id": "BTCUSDT",
# 	"type": "market",
# 	"side": "sell",
# 	"trigger_price": 29193,
# 	"price": "",
# 	"quantity": 0.000402,
# 	"client_order_id": "1690700243834"
# }

# take_profit_order = exchange.create_order ("BTCUSDT","Market","Sell","0.000402","",params)


# https://api2-1.bybit.com/spot/api/order/plan_spot/create

# {
# 	"symbol_id": "BTCUSDT",
# 	"type": "market",
# 	"side": "sell",
# 	"trigger_price": "29000",
# 	"price": "",
# 	"quantity": "0.000201",
# 	"client_order_id": "1690701864839"
# }

# The necessary param for perpetual conditional order is : "triggerPrice", "triggerDirection"

# print(get_session(TEST).place_order(
#     category="spot",
#     symbol="BTCUSDT",
#     side="Sell",
#     orderType="Market",
#     qty="0.000401",
#     triggerPrice="29000",
#     triggerDirection=0
# ))

httpClient=requests.Session()
recv_window=str(5000)
def HTTP_Request(endPoint,method,payload,Info):
    global time_stamp
    time_stamp=str(int(time.time() * 10 ** 3))
    signature=genSignature(payload)
    headers = {
        'X-BAPI-API-KEY': API_KEY,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if(method=="POST"):
        response = httpClient.request(method, BASE_URL+endPoint, headers=headers, data=payload)
    else:
        response = httpClient.request(method, BASE_URL+endPoint+"?"+payload, headers=headers)
    print(response.text)
    print(Info + " Elapsed Time : " + str(response.elapsed))

def genSignature(payload):
    param_str= str(time_stamp) + API_KEY + recv_window + payload
    hash = hmac.new(bytes(API_SECRET, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
    signature = hash.hexdigest()
    return signature


#Create Order
endpoint="/v5/order/create"
method="POST"
orderLinkId=uuid.uuid4().hex
params='{"category":"spot","symbol": "BTCUSDT","side": "Sell","orderType": "Market","qty": "0.000401" ,"price":"","orderFilter":"tpslOrder",  "triggerPrice":"28000"  ,"timeInForce": "GTC","orderLinkId": "' + orderLinkId + '"}'
HTTP_Request(endpoint,method,params,"Create")



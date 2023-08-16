import time
from bybitapi import check_closed_orders


def test_call_check_orders():        
    while True:
        try:
            check_closed_orders()
            time.sleep(30)
        except Exception as e:
            print(f"An error occurred: {e}")    

test_call_check_orders()
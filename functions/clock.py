import datetime
import os
import time
from bybitapi import get_server_time
from functions.logger import logger


def sync_system_clock():
    oldtime = datetime.datetime.now()
    servertime = get_server_time()
    newtime = datetime.datetime.fromtimestamp(float(servertime))

    os.system(f'sudo date --set="{newtime.strftime("%Y-%m-%d %H:%M:%S")}"')

    logger(f"Old time: {oldtime} New time: {datetime.datetime.now()}")

def call_decide_every_n_seconds(n, decide):
    """
    Function that calls the callback function `decide` every `n` seconds
    :param n: time interval in seconds
    :param decide: callback function to be called
    """
    while True:
        # Call the callback function
        decide()
        
        # Wait for n seconds
        time.sleep(n)




import datetime
import os
import time
from functions.logger import logger




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




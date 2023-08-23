from functions.logger import logger


import os
import time


def is_file_older_than_n_minutes(file_path, n):
    if ((file_path == None) or not os.path.exists(file_path)):
        logger("File doesnt exist")

        return True
    logger("time is ", time.time(), "|file time is",
           os.path.getmtime(file_path))
    return time.time() - os.path.getmtime(file_path) > n * 60
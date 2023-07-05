from TrainAndTest import retrain, trade_loop
from config import FORCERETRAINATSTART
from functions.clock import call_decide_every_n_seconds
from functions.logger import logger


if FORCERETRAINATSTART:
    logger("Force retrain at start set to true, retraining.")
    retrain()

call_decide_every_n_seconds(300, trade_loop)
from config import LOOKAHEADVALUE


def getHighs(data,row_position):
    return data.iloc[row_position:row_position+LOOKAHEADVALUE]['high']
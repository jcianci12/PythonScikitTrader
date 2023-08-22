from config import LOOKAHEADVALUE


def getLows(data,row_position):
    return data.iloc[row_position:row_position+LOOKAHEADVALUE]['low']
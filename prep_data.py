from config import LOOKAHEADVALUE

def _exponential_smooth(data, alpha):
    """
    Function that exponentially smooths dataset so values are less 'rigid'
    :param alpha: weight factor to weight recent values more
    """

    return data.ewm(alpha=alpha).mean()

def _produce_movement_indicators(data):
    """
    Function that produces the 'truth' values
    At a given row, it looks 'window' rows ahead to see if the price increased (1) or decreased (0)
    :param window: number of days, or rows to look ahead to see what the price did
    """

    predictionup = data.shift(-LOOKAHEADVALUE)["close"] >= data["close"]
    predictionup = predictionup.iloc[:-LOOKAHEADVALUE]
    data["pred"] = predictionup.astype(int)

    predictiondec = data.shift(-LOOKAHEADVALUE)["close"] <= data["close"]
    predictiondec = predictiondec.iloc[:-LOOKAHEADVALUE]
    data["preddec"] = predictiondec.astype(int)

    return data

def prep_data(data):
     #smooth the data
    data = _exponential_smooth(data,0.65)
    #produce indicators
    data = _produce_movement_indicators(data)
    #drop na data
    data = (
        data.dropna()
    )  # Some indicators produce NaN values for the first few rows, we just remove them here
    return data


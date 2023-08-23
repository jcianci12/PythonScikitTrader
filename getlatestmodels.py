import datetime
from imp import load_module
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from config import INTERVAL

from get_latest_model_file import get_latest_model_filename


def initialisemodels():

    latestFilename = get_latest_model_filename("BTCUSD", INTERVAL, "ensembleinc")
    if(latestFilename):
        rfinc , knninc , rfdec  , knndec ,estimatorsinc , estimatorsdec,ensembleinc ,ensembledec =load_module("models")
        
    else:

        # Models which will be used
        rfinc = RandomForestClassifier()
        knninc = KNeighborsClassifier()

        rfdec = RandomForestClassifier()
        knndec = KNeighborsClassifier()

        # Create a tuple list of our models
        estimatorsinc = [("knninc", knninc), ("rfinc", rfinc)]
        estimatorsdec = [("rfdec", rfdec), ("knndec", knndec)]

        ensembleinc = VotingClassifier(estimatorsinc, voting="soft")
        ensembledec = VotingClassifier(estimatorsdec, voting="soft")

    return rfinc , knninc , rfdec  , knndec ,estimatorsinc , estimatorsdec,ensembleinc ,ensembledec 


def parse_dates_from_file_name(s: str):
    parts = s.split("_")
    start_str = parts[2]
    end_str = parts[3]
    date_format = "%Y-%m-%d %H:%M:%S.%f"
    start_date = datetime.datetime.strftime(start_str, date_format)
    end_date = datetime.datetime.strptime(end_str, date_format)
    return start_date, end_date


import os
import joblib
from parse_file_name import parse_file_name
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

def load_latest_model():
    result = parse_file_name()
    if result is None:
        print(f'No .joblib files exist in the models folder.')
        return None
    start_date, end_date, symbol, interval = result
    file_name = f'{symbol}_{interval}_{start_date.strftime("%Y-%m-%d %H:%M:%S.%f")}_{end_date.strftime("%Y-%m-%d %H:%M:%S.%f")}.joblib'
    model = joblib.load(os.path.join('models', file_name))
    return model


def get_new_model():
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

        return rfinc,knninc,rfdec,knndec,estimatorsinc,estimatorsdec,ensembleinc,ensembledec
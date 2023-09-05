import os
from datetime import datetime


def parse_file_name():
    model_files = [f for f in os.listdir('models') if f.endswith('.joblib')]
    if not model_files:
        return None
    latest_file = max(model_files, key=lambda x: os.path.getmtime(os.path.join('models', x)))
    file_name = os.path.splitext(latest_file)[0]
    parts = file_name.split('_')
    symbol = parts[0]
    interval = parts[1]
    start_date = datetime.strptime(parts[2], '%Y-%m-%d %H:%M:%S.%f')
    end_date = datetime.strptime(parts[3], '%Y-%m-%d %H:%M:%S.%f')
    return start_date, end_date, symbol, interval



test = parse_file_name()
print(test)
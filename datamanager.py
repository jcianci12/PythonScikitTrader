from config import EXCLUDECOLUMNS, PREDCOLUMNS
from prep_data import prep_data


class DataManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._data = None
        return cls._instance

    @property
    def data(self):
        return self._data
    
    @property
    def trainingdata(self):
        data = prep_data(self._data)
        return data
    
    @property
    def tradingdata(self):
        data = prep_data(self._data)
        data = data.tail(1)
        data = data.drop(EXCLUDECOLUMNS+PREDCOLUMNS, axis=1)
        return data
    
    @property
    def sampledata(self):
        data = self._data.tail(1).to_string()

        return data

    @data.setter
    def data(self, new_data):
        self._data = new_data

# # Example usage:

# # Create instances of DataManager
# data_manager1 = DataManager()
# data_manager2 = DataManager()

# # Set data using the setter on one instance
# data_manager1.data = "Hello, World!"

# # Get data using the getter on another instance
# print(data_manager2.data)  # Output: Hello, World!

class CapitalTracker:
    def __init__(self, initial_capital=0):
        self.capital = initial_capital

    def spend(self, amount):
        if amount > self.capital:
            return False, "Insufficient funds. Transaction failed."
        self.capital -= amount
        return True, f"Spent {amount}. Remaining capital: {self.capital}."

    def earn(self, amount):
        self.capital += amount
        return True, f"Earned {amount}. Updated capital: {self.capital}."


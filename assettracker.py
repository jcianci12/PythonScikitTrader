from capitaltracker import CapitalTracker

class Asset:
    def __init__(self, quantity, purchase_price, take_profit, stop_loss):
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.sell_price = 0


class AssetTracker:
    def __init__(self, initial_capital=10000):
        self.inventory = []
        self.total_profit = 0
        self.average_profit = None
        self.success_ratio = 0.5
        # self.capital_tracker = CapitalTracker(initial_capital)

    def success(self, profit):
        return (profit + self.success_ratio) / 2



    def set_avg_profit(self, profit):
        if self.average_profit is None:
            self.average_profit = profit
        self.average_profit = (self.average_profit + profit) / 2

    def purchase(self, quantity, purchase_price, take_profit, stop_loss):       

        asset = Asset(quantity, purchase_price, take_profit, stop_loss)
        self.inventory.append(asset)

        return {
            "message": f"Purchased {quantity} Assets at price {purchase_price}",
            "avgprof": self.average_profit,
        }

    def sell(self, quantity, sell_price):
        if len(self.inventory) == 0:            
            return False, f"No Assets in inventory to sell."


        remaining_quantity = quantity
        while remaining_quantity > 0 and len(self.inventory) > 0:
            asset = self.inventory[0]

            if asset.quantity <= remaining_quantity:
                # Sell the entire asset
                remaining_quantity -= asset.quantity
                asset.sell_price = sell_price
                profit = (sell_price - asset.purchase_price) * asset.quantity
                self.total_profit += profit
                self.set_avg_profit(profit)
                self.success_ratio = self.success(profit)

                position_size = self.get_total_asset_quantity()
                self.inventory.pop(0)
                return {
                    "asset": asset.quantity,
                    "profit": profit,
                    "avgprof": self.average_profit,
                    "total_prof": self.total_profit,
                    "successratio": self.success_ratio,
                }
            else:
                # Sell a partial asset
                asset.quantity -= remaining_quantity
                asset.sell_price = sell_price
                profit = (sell_price - asset.purchase_price) * remaining_quantity
                self.total_profit += profit
                self.set_avg_profit(profit)
                self.success_ratio = self.success(profit)
                remaining_quantity = 0
                return {
                    "asset": asset.quantity,
                    "profit": profit,
                    "avgprof": self.average_profit,
                    "total_prof": self.total_profit,
                    "successratio": self.success_ratio,
                }
    def monitor_prices(self, current_price):
        triggered_assets = []

        for asset in self.inventory:
            if asset.sell_price == 0:
                if current_price >= asset.take_profit:
                    triggered_assets.append(asset)
                elif current_price <= asset.stop_loss:
                    triggered_assets.append(asset)

        return triggered_assets
            

    def get_total_asset_quantity(self):
        total_quantity = 0
        for asset in self.inventory:
            total_quantity += asset.quantity
        return total_quantity

    def calculate_total_profit(self):
        return self.total_profit
    def getSuccessRatio(self):
        if self.success_ratio is None:
            return 0.5
        else:
            return self.success_ratio

    

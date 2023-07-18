import csv
import time
from config import ORDERCSVFIELDNAMES


class OrderService:
    orders = []

    def read_orders(self):
        # Load the orders from the CSV file
        with open('orders.csv', mode='r') as orders_file:
            reader = csv.DictReader(orders_file)
            self.orders = list(reader)
            return self.orders

    def add_order(self,order):
        listtoupdate = self.read_orders().copy()
        listtoupdate.append(order)
        self.write_orders('orders.csv',listtoupdate)

    def write_orders(self,filename, neworders):
        # Write updated data to CSV file
        if(self.orders!=neworders):
            with open(filename, mode='w') as file:
                writer = csv.DictWriter(file, fieldnames=ORDERCSVFIELDNAMES)
                writer.writeheader()
                writer.writerows(neworders)

    


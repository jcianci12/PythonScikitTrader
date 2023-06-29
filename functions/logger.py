import datetime

from config import TEST

def logger(*args):
    now = datetime.now()
    message = ' '.join(map(str, args))
    training = "TRAINING MODE " if TEST else "REAL MODE"
    log_message = f'{now}: {training} {message}'
    print("logging",log_message)
    with open('log.txt', 'a') as file:
        file.write(   log_message + '\n')

import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_graph(btc_price, confidence_signal, portfolio_balance,usdtbalance,btcbalance, chartfilename,csvfilename, viewwindow):
    if(viewwindow==None):
        viewwindow = 10000
    # Check if the performance.csv file exists
    if not os.path.exists(csvfilename):
        # If the file doesn't exist, create it and write the header row
        with open(csvfilename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Datetime', 'BTC Price', 'Confidence Signal', 'Portfolio','USDT','BTC'])
    
    # Get the current datetime value
    current_datetime = datetime.now()
    
    # Append the data to the performance.csv file
    with open(csvfilename, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([current_datetime, btc_price, confidence_signal, portfolio_balance,usdtbalance,btcbalance])
    
    # Read the data from the performance.csv file
    with open(csvfilename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        data = [row for row in reader]
    
    # Extract the data from the CSV file
    datetime_values = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f') for row in data]
    btc_price = [float(row[1]) for row in data]
    confidence_signal = [float(row[2]) for row in data]
    portfolio_balance = [float(row[3]) for row in data]
    usdtbalance = [float(row[4]) for row in data]
    btcbalance = [float(row[5]) for row in data]

    
    # Create a figure and three subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    
    # Plot the BTC price data on the first subplot
    ax1.plot(datetime_values[-viewwindow:], btc_price[-viewwindow:], label='BTC Price')
    
    # Plot the confidence signal data on the second subplot
    ax2.plot(datetime_values[-viewwindow:], confidence_signal[-viewwindow:], label='Confidence Signal', color='g')
    
    # Plot the current balance data on the third subplot
    ax3.plot(datetime_values[-viewwindow:], portfolio_balance[-viewwindow:], label='Current Balance', color='r')
    ax3.plot(datetime_values[-viewwindow:], usdtbalance[-viewwindow:], label='USDT Balance', color='b')
    ax3.plot(datetime_values[-viewwindow:], btcbalance[-viewwindow:], label='BTC Balance', color='g')
    
    # Format the x-axis of each subplot to display datetime values
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    
    # Add labels and title to each subplot
    ax1.set_xlabel('Datetime')
    ax1.set_ylabel('BTC Price')
    ax2.set_xlabel('Datetime')
    ax2.set_ylabel('Confidence Signal')
    ax3.set_xlabel('Datetime')
    ax3.set_ylabel('Current Balance')
    
    # Add a legend to each subplot
    ax1.legend()
    ax2.legend()
    ax3.legend()
    
    # Save the plot to a file
    plt.savefig(chartfilename)
    plt.close()
    


import pandas as pd #data manipulation and analysis package
from alpha_vantage.timeseries import TimeSeries #enables data pull from Alpha Vantage
import matplotlib.pyplot as plt #if you want to plot your findings
import time
import smtplib #enables you to send emails
import sqlite3

def convert_db_to_dict(database_file):
    conn = sqlite3.connect(database_file)  # Connect to the database
    cursor = conn.cursor()

    # Execute a SELECT statement to retrieve data from the table
    cursor.execute("SELECT * FROM posts")
    rows = cursor.fetchall()

    # Define an empty dictionary to store the converted data
    result = {}

    # Iterate over the rows and convert them to dictionary entries
    for row in rows:
        key = row[0]  # Assuming the first column as the key
        values = row[1:]  # Assuming remaining columns as values

        result[key] = values

    conn.close()  # Close the database connection

    return result

def check_database_stocks(dict, name):
    for key, value in dict.items():
        if name == value[1]:
            print("Key:", key)
            print("Ticket:", value[3])
            print("Ceiling:", value[4])
            print("Floor:", value[5])
            print("---")
            ceil = int(value[4])
            floor = int(value[5])
            ts = TimeSeries(key='BDSDZZ3QYDLK7XKF', output_format='pandas')
            data, meta_data = ts.get_intraday(symbol=value[3],interval='5min', outputsize='full')
            #We are currently interested in the latest price
            close_data = data['4. close'] #The close data column
            last_price = close_data[0] #Selecting the last price from the close_data column
            if (last_price < floor) or (last_price > ceil):
                print("boundary alert!!!")

    # return dict

database_file = 'database.db'
dictionary = convert_db_to_dict(database_file)
print(dictionary)
title_u = input("Enter title: ")
check_database_stocks(dictionary, title_u)


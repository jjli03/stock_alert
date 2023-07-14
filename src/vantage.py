from operator import truediv
import pandas as pd #data manipulation and analysis package
from alpha_vantage.timeseries import TimeSeries #enables data pull from Alpha Vantage
# import matplotlib.pyplot as plt #if you want to plot your findings
import time
# import smtplib #enables you to send emails.
import requests

def price_setup(ticket):
    ts = TimeSeries(key='3USNE3HPB4IZQIL8', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=ticket,interval='5min', outputsize='full')
    close_data = data['4. close']
    return close_data[0]

def extract_prices(posts):
    price_list = []
    for post in posts:
        ticket = post[4]
        last_price = price_setup(ticket)  # Selecting the last price from the close_data column
        price_list.append(last_price)
    return price_list

def check_database_stocks(dict, name, ticket): # Return -1 for name not found, 0 for no alert, 1 for alert
    for key, value in dict.items():
        if (name == value[1]) and (ticket == value[3]):
            ceil = int(value[4])
            floor = int(value[5])
            last_price = price_setup(value[3]) #Selecting the last price from the close_data column
            if (last_price < floor) or (last_price > ceil):
                return last_price
    return -1

def validate_ticket(ticket):
    try:
        last_price = price_setup(ticket)
        return True
    except:
        return False
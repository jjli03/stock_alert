import pandas as pd #data manipulation and analysis package
from alpha_vantage.timeseries import TimeSeries #enables data pull from Alpha Vantage
import matplotlib.pyplot as plt #if you want to plot your findings
import time
import smtplib #enables you to send emails

val = input("Enter valid ticker symbol: ")
# trgt = input("Target sell price: ")
#Getting the data from alpha_vantage
ts = TimeSeries(key='BDSDZZ3QYDLK7XKF', output_format='pandas')
data, meta_data = ts.get_intraday(symbol=val,interval='5min', outputsize='full')
#We are currently interested in the latest price
close_data = data['4. close'] #The close data column
last_price = close_data[0] #Selecting the last price from the close_data column
#Check if you're getting a correct value
avg_cprice = 0
price_num1 = 0
for i in close_data:
    avg_cprice += i
    price_num1 += 1
print('closing price today:', last_price)
print('average closing price:', round((avg_cprice / price_num1), 2))
print(' ')
print(data)
#Set the desired message you want to see once the stock price is at a certain level
# sender_email = "youremail@email.com" #The sender email
# rec_email = "receivingemail@email.com" #The receiver email
# password = ("password") #The password to the sender email
# message = "MSFT STOCK ALERT!!! The stock is at above price you set " + "%.6f" % last_price  #The message you want to send
# target_sell_price = 220 #enter the price you want to sell at
# if last_price > target_sell_price:
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     server.login(sender_email, password) #logs into your email account
#     print("Login Success") #confirms that you have logged in succesfully
#     server.sendmail(sender_email, rec_email, message) #send the email with your custom mesage
#     print("Email was sent") #confirms that the email was sent 
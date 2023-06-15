import pandas as pd #data manipulation and analysis package
from alpha_vantage.timeseries import TimeSeries #enables data pull from Alpha Vantage
# import matplotlib.pyplot as plt #if you want to plot your findings
import time
# import smtplib #enables you to send emails

import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

from datmod import get_alerts_with_ticket, get_alerts_with_title

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_post_name(post_name, post_tic):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE title = ? AND ticket = ?',
                        (post_name, post_tic)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

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

def check_database_stocks(dict, name): # Return -1 for name not found, 0 for no alert, 1 for alert
    for key, value in dict.items():
        if name == value[1]:
            # print("Key:", key)
            # print("Ticket:", value[3])
            # print("Ceiling:", value[4])
            # print("Floor:", value[5])
            # print("---")
            ceil = int(value[4])
            floor = int(value[5])
            ts = TimeSeries(key='BDSDZZ3QYDLK7XKF', output_format='pandas')
            data, meta_data = ts.get_intraday(symbol=value[3],interval='5min', outputsize='full')
            #We are currently interested in the latest price
            close_data = data['4. close'] #The close data column
            last_price = close_data[0] #Selecting the last price from the close_data column
            if (last_price < floor) or (last_price > ceil):
                #print("boundary alert!!!")
                return last_price
    return -1

# --- Web Endpoints ---

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/alert/<title>')
def alert(title):
    conn = get_db_connection()
    #alerts = conn.execute('SELECT * FROM alerts WHERE title = ?', ([title])).fetchall()
    alerts = get_alerts_with_title(title)
    conn.close()
    return render_template('alert.html', alerts=alerts)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        email = request.form['email']
        ticket = request.form['ticket']
        ceilings = request.form['ceilings']
        floors = request.form['floors']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, email, ticket, ceilings, floors) VALUES (?, ?, ?, ?, ?)',
                         (title, email, ticket, ceilings, floors))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        email = request.form['email']
        ticket = request.form['ticket']
        ceilings = request.form['ceilings']
        floors = request.form['floors']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, email = ?, ticket = ?, ceilings = ?, floors = ?' 
                         ' WHERE id = ?',
                         (title, email, ticket, ceilings, floors, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/checks', methods=('GET', 'POST'))
def checks():
    if request.method == 'POST':
        title = request.form['title']
        ticket = request.form['ticket']

        if not title:
            flash('Title is required!')
        else:
            dictionary = convert_db_to_dict("database.db")
            pricing = check_database_stocks(dictionary, title)
            if pricing >= 0:
                flash("stock alerts")
                conn = get_db_connection()
                conn.execute('INSERT INTO alerts (title, ticket, price) VALUES (?, ?, ?)',
                            (title, ticket, pricing))
                conn.commit()
                conn.close()
            else:
                flash("no stock alerts detected")
            alerts = get_alerts_with_ticket(title, ticket)
            return render_template('alert.html', alerts=alerts)

    return render_template('checks.html')
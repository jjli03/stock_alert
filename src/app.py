import pandas as pd #data manipulation and analysis package
from alpha_vantage.timeseries import TimeSeries #enables data pull from Alpha Vantage
# import matplotlib.pyplot as plt #if you want to plot your findings
import time
# import smtplib #enables you to send emails

import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user
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

def get_alert(alert_id):
    conn = get_db_connection()
    alert = conn.execute('SELECT * FROM alerts WHERE id = ?',
                        (alert_id,)).fetchone()
    conn.close()
    if alert is None:
        abort(404)
    return alert

def convert_db_to_dict(database_file):
    conn = sqlite3.connect(database_file)  # Connect to the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    rows = cursor.fetchall()
    result = {}
    for row in rows:
        key = row[0]  # Assuming the first column as the key
        values = row[1:]  # Assuming remaining columns as values
        result[key] = values
    conn.close()  # Close the database connection
    return result

def price_setup(ticket):
    ts = TimeSeries(key='3USNE3HPB4IZQIL8', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=ticket,interval='5min', outputsize='full')
    close_data = data['4. close']
    return close_data[0]

def extract_prices(posts):
    #ts = TimeSeries(key='3USNE3HPB4IZQIL8', output_format='pandas')
    price_list = []
    for post in posts:
        ticket = post[4]
        # data, meta_data = ts.get_intraday(symbol=ticket, interval='5min', outputsize='full')
        # close_data = data['4. close']  # The close data column
        last_price = price_setup(ticket)  # Selecting the last price from the close_data column
        price_list.append(last_price)
    return price_list

def check_database_stocks(dict, name, ticket): # Return -1 for name not found, 0 for no alert, 1 for alert
    for key, value in dict.items():
        if (name == value[1]) and (ticket == value[3]):
            ceil = int(value[4])
            floor = int(value[5])
            #print(value[3])
            # ts = TimeSeries(key='3USNE3HPB4IZQIL8', output_format='pandas')
            # data, meta_data = ts.get_intraday(symbol=value[3],interval='5min', outputsize='full')
            # #We are currently interested in the latest price
            # close_data = data['4. close'] #The close data column
            last_price = price_setup(value[3]) #Selecting the last price from the close_data column
            if (last_price < floor) or (last_price > ceil):
                return last_price
    return -1

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['SECRET_KEY'] = 'your secret key'

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

# Create user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
    email = db.Column(db.String(250),
                         nullable=False)
 
 
# Initialize app with extension
db.init_app(app)
# Create database within app context
 
with app.app_context():
    db.create_all()

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

# --- Web Endpoints ---

@app.route("/")
def home():
    # Render home.html on "/" route
    return render_template("home.html")

@app.route('/index')
@login_required
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=["GET", "POST"])
def register():
  # If the user made a POST request, create a new user
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     email=request.form.get("email"),
                     password=request.form.get("password"))
        # Add the user to the database
        db.session.add(user)
        # Commit the changes made
        db.session.commit()
        # Once user account created, redirect them
        # to login route (created later on)
        return redirect(url_for("login"))
    # Renders sign_up template if user made a GET request
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # If a post request was made, find the user by
    # filtering for the username
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        # Check if the password entered is the
        # same as the user's password
        if user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            login_user(user)
            return redirect(url_for("myposts"))
        # Redirect the user back to the home
        # (we'll create the home route in a moment)
    return render_template("login.html")

# @app.route('/alert/<title>')
# @login_required
# def alert(title):
#     conn = get_db_connection()
#     alerts = get_alerts_with_title(title)
#     conn.close()
#     return render_template('alert.html', alerts=alerts)

@app.route('/myposts')
@login_required
def myposts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts WHERE title = ?',
                        (current_user.username,)).fetchall()
    prices_list = extract_prices(posts)
    conn.close()
    return render_template('index.html', posts=posts, prices=prices_list)

@app.route('/<int:post_id>')
@login_required
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = current_user.username
        email = current_user.email
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
            return redirect(url_for('myposts'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = current_user.username
        email = current_user.email
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
            return redirect(url_for('myposts'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/checks', methods=('GET', 'POST'))
@login_required
def checks():
    if request.method == 'POST':
        title = current_user.username
        tickets_input = request.form['ticket']
        tickets = [ticket.strip() for ticket in tickets_input.split(',')]

        if not title:
            flash('Title is required!')
        else:
            dictionary = convert_db_to_dict("database.db")
            for ticket in tickets:
                pricing = check_database_stocks(dictionary, title, ticket)
                if pricing >= 0:
                    conn = get_db_connection()
                    conn.execute('INSERT INTO alerts (title, ticket, price) VALUES (?, ?, ?)',
                                (title, ticket, pricing))
                    conn.commit()
                    conn.close()
                else:
                    flash("No stock alerts detected for ticket: " + ticket)
            
            alerts = get_alerts_with_ticket(title, tickets)
            return render_template('alert.html', alerts=alerts)

    return render_template('checks.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run()
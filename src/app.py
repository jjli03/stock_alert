import sqlite3
from vantage import price_setup, extract_prices, check_database_stocks, validate_ticket
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.exceptions import abort

from datmod import get_alerts_with_ticket, get_alerts_with_title
from sqlite_db import SqlLiteDb
from usermod import Users, db
import requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['SECRET_KEY'] = 'your secret key'

db_manager = SqlLiteDb('database.db')

login_manager = LoginManager()
login_manager.init_app(app)
 
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
    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
  # If the user made a POST request, create a new user
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     email=request.form.get("email"),
                     password=request.form.get("password"))
        # Add the user to the database
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html")

from flask import flash

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        
        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for("myposts"))
            else:
                flash("Incorrect password. Please try again.", "error")
        else:
            flash("User not found. Please try again.", "error")
    
    return render_template("login.html")

@app.route('/myposts')
@login_required
def myposts():
    posts = db_manager.get_post_name(current_user.username)
    prices_list = extract_prices(posts)
    return render_template('index.html', posts=posts, prices=prices_list)

# @app.route('/<int:post_id>')
# @login_required
# def post(post_id):
#     post = db_manager.get_post(post_id)
#     return render_template('post.html', post=post)

@app.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = current_user.username
        email = current_user.email
        ticket = request.form['ticket']
        ceilings = request.form['ceilings']
        floors = request.form['floors']

        if not title: # Error handling if ceiling/floor are numbers, ceiling > floor, and 
            flash('Title is required!', 'error') # the ticekt is valid according to vantage
        elif not ceilings.isdigit() or not floors.isdigit():
            flash('Ceilings and floors must be numbers!', 'error')
        elif int(ceilings) <= int(floors):
            flash('Ceilings must be greater than floors!', 'error')
        elif not validate_ticket(ticket):
            flash('Invalid stock ticket symbol!', 'error')
        else:
            db_manager.create_post(title, email, ticket, ceilings, floors)
            return redirect(url_for('myposts'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    post = db_manager.get_post(id)

    if request.method == 'POST':
        title = current_user.username
        email = current_user.email
        ticket = request.form['ticket']
        ceilings = request.form['ceilings']
        floors = request.form['floors']

        if not title: # Error handling if ceiling/floor are numbers, ceiling > floor, and 
            flash('Title is required!', 'error') # the ticekt is valid according to vantage
        elif not ceilings.isdigit() or not floors.isdigit():
            flash('Ceilings and floors must be numbers!', 'error')
        elif int(ceilings) <= int(floors):
            flash('Ceilings must be greater than floors!', 'error')
        elif not validate_ticket(ticket):
            flash('Invalid stock ticket symbol!', 'error')
        else:
            db_manager.update_post(title, email, ticket, ceilings, floors, id)
            return redirect(url_for('myposts'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = db_manager.get_post(id)
    db_manager.delete_post(id)
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('myposts'))

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
            dictionary = db_manager.convert_db_to_dict()
            for ticket in tickets:
                pricing = check_database_stocks(dictionary, title, ticket)
                if pricing >= 0:
                    db_manager.create_alert(title, ticket, pricing)
                else:
                    flash("No stock alerts detected for ticket: " + ticket)
            
            alerts = get_alerts_with_ticket(title, tickets)
            return render_template('alert.html', alerts=alerts)

    return render_template('checks.html')

@app.route('/clear', methods=['GET', 'POST'])
@login_required
def clear():
    if request.method == 'POST':
        table = request.form.get('table')
        if table == 'posts':
            db_manager.clear_posts()
        elif table == 'alerts':
            db_manager.clear_alerts()
        return redirect(url_for('myposts'))
    return render_template('clear.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run()
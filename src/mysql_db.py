import pymysql
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.exceptions import abort

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Potomac_11'
)

# Create a new MySQL database
db_name = 'newt'
cursor = connection.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
connection.commit()
cursor.close()
connection.close()

# Connect to the newly created database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Potomac_11',
    db=db_name
)

# Create the 'posts' table
cursor = connection.cursor()
create_posts_table = '''
    CREATE TABLE IF NOT EXISTS posts (
        id INT PRIMARY KEY AUTO_INCREMENT,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        title TEXT NOT NULL,
        email TEXT NOT NULL,
        ticket TEXT NOT NULL,
        ceilings TEXT NOT NULL,
        floors TEXT NOT NULL
    )
'''
cursor.execute(create_posts_table)
connection.commit()

# Create the 'alerts' table
create_alerts_table = '''
    CREATE TABLE IF NOT EXISTS alerts (
        alert_id INT PRIMARY KEY AUTO_INCREMENT,
        alert_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        title TEXT NOT NULL,
        ticket TEXT NOT NULL,
        price TEXT NOT NULL
    )
'''
cursor.execute(create_alerts_table)
connection.commit()

cursor.close()
connection.close()

# --- Classes ---

class Post:
    def __init__(self, id, created, title, email, ticket, ceilings, floors):
        self.id = id
        self.created = created
        self.title = title
        self.email = email
        self.ticket = ticket
        self.ceilings = ceilings
        self.floors = floors


class Alert:
    def __init__(self, alert_id, alert_time, title, ticket, price):
        self.alert_id = alert_id
        self.alert_time = alert_time
        self.title = title
        self.ticket = ticket
        self.price = price


class User(UserMixin):
    def __init__(self, id):
        self.id = id

class MySqlDb:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db

    def connect(self):
        return pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db)

    def get_post(self, post_id):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = %s', (post_id,))
        result = cursor.fetchone()
        connection.close()
        if result is None:
            abort(404)
        post_data = {
            'id': result[0],      # id
            'created': result[1], # created
            'title': result[2],   # title
            'email': result[3],   # email
            'ticket': result[4],  # ticket
            'ceilings': result[5], # ceilings
            'floors': result[6]   # floors
        }
        return post_data

    def get_post_name(self, title):
        connection = self.connect()
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT * FROM posts WHERE title = %s', (title,))
            result = cursor.fetchall()
        except Exception as e:
            # Handle the exception, such as logging or printing the error
            print("Error:", e)
            result = []
        connection.close()
        posts = []
        for row in result:
            post_data = {
                'id': row[0],      # id
                'created': row[1], # created
                'title': row[2],   # title
                'email': row[3],   # email
                'ticket': row[4],  # ticket
                'ceilings': row[5], # ceilings
                'floors': row[6]   # floors
            }
            posts.append(post_data)
        return posts

    def convert_db_to_dict(self):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        connection.close()
        result = {}
        for row in rows:
            key = row[0]
            values = row[1:]
            result[key] = values
        return result

    def create_post(self, title, email, ticket, ceilings, floors):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO posts (title, email, ticket, ceilings, floors) VALUES (%s, %s, %s, %s, %s)',
                       (title, email, ticket, ceilings, floors))
        connection.commit()
        connection.close()

    def update_post(self, title, email, ticket, ceilings, floors, post_id):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute('UPDATE posts SET title = %s, email = %s, ticket = %s, ceilings = %s, floors = %s WHERE id = %s',
                       (title, email, ticket, ceilings, floors, post_id))
        connection.commit()
        connection.close()

    def delete_post(self, post_id):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM posts WHERE id = %s', (post_id,))
        connection.commit()
        connection.close()

    def create_alert(self, title, ticket, price):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO alerts (title, ticket, price) VALUES (%s, %s, %s)',
                       (title, ticket, price))
        connection.commit()
        connection.close()

    def clear_posts(self):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM posts')
        connection.commit()
        connection.close()

    def clear_alerts(self):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM alerts')
        connection.commit()
        connection.close()


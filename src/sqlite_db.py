import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.exceptions import abort

from datmod import get_alerts_with_ticket, get_alerts_with_title

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

# cur = connection.cursor()

# cur.execute("INSERT INTO posts (title, email, ticket, ceilings, floors) VALUES (?, ?, ?, ?, ?)",
#             ('Michael', 'michael1234@yahoo.com', 'NDAQ', 200, 100)
#             )

# cur.execute("INSERT INTO alerts (title, ticket, price) VALUES (?, ?, ?)",
#             ('Tammy', 'MSFT', 123)
#             )

connection.commit()
connection.close()

class SqlLiteDb:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def get_post(self, post_id):
        self.connect()
        post = self.cursor.execute('SELECT * FROM posts WHERE id = ?',
                                   (post_id,)).fetchone()
        self.disconnect()
        if post is None:
            abort(404)
        return post

    def get_post_name(self, title):
        self.connect()
        post = self.cursor.execute('SELECT * FROM posts WHERE title = ?',
                                   (title,)).fetchall()
        self.disconnect()
        if post is None:
            abort(404)
        return post

    def convert_db_to_dict(self):
        self.connect()
        self.cursor.execute("SELECT * FROM posts")
        rows = self.cursor.fetchall()
        result = {}
        for row in rows:
            key = row[0]
            values = row[1:]
            result[key] = values
        self.disconnect()
        return result

    def create_post(self, title, email, ticket, ceilings, floors):
        self.connect()
        self.cursor.execute('INSERT INTO posts (title, email, ticket, ceilings, floors) VALUES (?, ?, ?, ?, ?)',
                            (title, email, ticket, ceilings, floors))
        self.connection.commit()
        self.disconnect()

    def update_post(self, title, email, ticket, ceilings, floors, post_id):
        self.connect()
        self.cursor.execute('UPDATE posts SET title = ?, email = ?, ticket = ?, ceilings = ?, floors = ? '
                            'WHERE id = ?',
                            (title, email, ticket, ceilings, floors, post_id))
        self.connection.commit()
        self.disconnect()

    def delete_post(self, post_id):
        self.connect()
        self.cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        self.connection.commit()
        self.disconnect()

    def create_alert(self, title, ticket, price):
        self.connect()
        self.cursor.execute('INSERT INTO alerts (title, ticket, price) VALUES (?, ?, ?)',
                            (title, ticket, price))
        self.connection.commit()
        self.disconnect()

    def clear_posts(self):
        self.connect()
        self.cursor.execute('DELETE FROM posts')
        self.connection.commit()
        self.disconnect()

    def clear_alerts(self):
        self.connect()
        self.cursor.execute('DELETE FROM alerts')
        self.connection.commit()
        self.disconnect()

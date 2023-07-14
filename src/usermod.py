from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user

db = SQLAlchemy()

# Create user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
    email = db.Column(db.String(250),
                         nullable=False)
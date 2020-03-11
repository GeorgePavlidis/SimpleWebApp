from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy

# ==================================================================================================
# Application Initialization
# ==================================================================================================
application = Flask(__name__)
application.config['SQLALCHEMY_TRACK_MODIFICATIONS '] = False
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(application)
g.token = 'thisissecret'
application.config['SECRET_KEY'] = g.token


# ==================================================================================================
# Define Databases Tables
# ==================================================================================================
# User Table
class User(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   publicId = db.Column(db.String(50), unique=True)
   username = db.Column(db.String(50))
   password = db.Column(db.String(80))


# Transaction Table
class Transaction(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   amount = db.Column(db.Float())
   income = db.Column(db.Boolean)
   date = db.Column(db.DateTime, default=datetime.utcnow)
   category = db.Column(db.String(80))
   userId = db.Column(db.Integer)

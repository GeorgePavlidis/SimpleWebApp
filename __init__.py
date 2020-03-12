from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# ==================================================================================================
# Application Initialization
# ==================================================================================================
application = Flask(__name__)
application.config['SQLALCHEMY_TRACK_MODIFICATIONS '] = False
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(application)
application.config['SECRET_KEY'] = 'thisissecret'
application.config['MODE'] = 4


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

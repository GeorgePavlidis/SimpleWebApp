from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


# ==================================================================================================
# Application Initialization
# ==================================================================================================
application = Flask(__name__)
application.config['SQLALCHEMY_TRACK_MODIFICATIONS '] = False
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(application)

# ==================================================================================================
# TEMPORARY CODE BLOCK
# ==================================================================================================
application.config['SECRET_KEY'] = 'thisissecret'


def token_required(f):
   @wraps(f)
   def decorated(*args, **kwargs):
      token = None

      if 'x-access-token' in request.headers:
         token = request.headers['x-access-token']

      if not token:
         return jsonify({'message': 'Token is missing!'}), 401

      try:
         data = jwt.decode(token, app.config['SECRET_KEY'])
         current_user = User.query.filter_by(public_id=data['public_id']).first()
      except:
         return jsonify({'message': 'Token is invalid!'}), 401

      return f(current_user, *args, **kwargs)

   return decorated


# ==================================================================================================
# Define Databases Tables
# ==================================================================================================
class User(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   publicId = db.Column(db.String(50), unique=True)
   username = db.Column(db.String(50))
   password = db.Column(db.String(80))


class Transaction(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   amount = db.Column(db.Float())
   income = db.Column(db.Boolean)
   date = db.Column(db.DateTime, default=datetime.utcnow)
   category = db.Column(db.String(80))
   userId = db.Column(db.Integer)


# ==================================================================================================
# Entry Points
# ==================================================================================================
@application.route('/')
def index():
   return redirect('/home')


@application.route('/user', methods=['POST'])
def createUser():
   return "createUser"


@application.route('/user/<public_id>', methods=['GET'])
def getOneUser(current_user, public_id):
   user = User.query.filter_by(id=public_id).first()
   userData = {
      'publicId': user.publicId,
      'username': user.username,
      'password': user.password,
   }
   return jsonify({'users': userData})


@application.route('/user/', methods=['GET'])
def getAllUsers():
   users = User.query.all()

   output = []

   for user in users:
      userData = {
         'publicId': user.publicId,
         'username': user.username,
         'password': user.password,
      }
      output.append(userData)

   return jsonify({'users': output})


@application.route('/user/<public_id>', methods=['DELETE'])
def deleteUser(current_user, public_id):

   if not current_user.id == public_id:
      return jsonify({'message': "Fail to delete this user: Only the owner of this account can "
                                 "delete it!"}),401

   user = User.query.filter_by(id=public_id).first()
   transs = Transaction.query.filter_by(user_id=current_user.id).all()

   db.session.delete(user)
   db.session.delete(transs)
   db.session.commit()

@application.route('/login')
def login():
   return "login"


@application.route('/home', methods=['GET'])
def createGraph():
   return 'createGraph'


@application.route('/home/<int:index>', methods=['GET'])
def changeMode():
   return "changeMode"


@application.route('/trans ', methods=['POST'])
@token_required
def addTransaction(current_user):
   data = request.get_json()

   newTransaction = Transaction(amount=data['amount'],
                                income=data['income'],
                                date=data['date'],
                                category=data['category'],
                                userId=current_user.id)

   db.session.add(newTransaction)
   db.session.commit()

   return jsonify({'message': "Transaction saved!"})


@application.route('/trans/<trans_id>', methods=['DELETE'])
def removeTransaction(current_user, trans_id):
   trans = Transaction.query.filter_by(id=trans_id, user_id=current_user.id).first()

   if not trans:
      return jsonify({'message': 'No transaction found!'})

   db.session.delete(trans)
   db.session.commit()


@application.route('/trans/<trans_id>', methods=['GET'])
def getOneTransaction(current_user, trans_id):
   trans = Transaction.query.filter_by(id=trans_id, user_id=current_user.id).first()

   transactionData = {'amount': trans.amount}
   if not trans.income:
      transactionData['amount'] = -1 * transactionData['amount']
   transactionData['date'] = trans.date
   transactionData['category'] = trans.category

   return jsonify({'transaction': transactionData})


@application.route('/trans/', methods=['GET'])
def getAllTransactions(current_user):
   transs = Transaction.query.filter_by(user_id=current_user.id).all()

   output = []
   for trans in transs:
      transactionData = {'amount': trans.amount}
      if not trans.income:
         transactionData['amount'] = -1 * transactionData['amount']
      transactionData['date'] = trans.date
      transactionData['category'] = trans.category
      output.append(transactionData)

   return jsonify({'transactions': output})


if __name__ == '__main__':
   application.run(debug=True)

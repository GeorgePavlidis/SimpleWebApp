from flask import Flask, jsonify, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from matplotlib import pyplot as plt

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

      if 'token' in request.headers:
         token = request.headers['token']

      if not token:
         return jsonify({'message': 'Token is missing!'}), 401

      try:
         data = jwt.decode(token, application.config['SECRET_KEY'])
         current_user = User.query.filter_by(publicId=data['publicId']).first()
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
   data = request.get_json()
   print ('password', data)

   print ('password', data['password'])
   print ('username', data['username'])
   hashedPass = generate_password_hash(data['password'], method='sha256')

   newUser = User(publicId=str(uuid.uuid4()),
                  username=data['username'],
                  password=hashedPass)

   db.session.add(newUser)
   db.session.commit()
   return jsonify({'message' : 'New user created!'})



@application.route('/user/<public_id>', methods=['GET'])
def getOneUser(public_id):
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
         'ID': user.id,
         'publicId': user.publicId,
         'username': user.username,
         'password': user.password,
      }
      output.append(userData)

   return jsonify({'users': output})


@application.route('/user/<int:public_id>', methods=['DELETE'])
@token_required
def deleteUser(current_user, public_id):
   if not current_user.id == public_id:
      return jsonify({'message': "Fail to delete this user: Only the owner of this account can "
                                 "delete it!"}),401

   user = User.query.filter_by(id=public_id).first()
   Transaction.query.filter_by(userId=current_user.id).delete()

   db.session.delete(user)
   db.session.commit()
   return jsonify({'message' : 'The user deleted!'})


@application.route('/login')
def login():
   auth = request.authorization
   if not auth or not auth.username or not auth.password:
      return make_response('Could not verify',
                          401,
                          {'WWW-Authenticate' : 'Basic realm="Login required!"'})

   user = User.query.filter_by(username=auth.username).first()

   if not user:
       return make_response('Could not verify',
                           401,
                           {'WWW-Authenticate' : 'Basic realm="Login required!"'})

   if check_password_hash(user.password, auth.password):
      token = jwt.encode({'publicId' : user.publicId,
                          'exp' : datetime.utcnow() + timedelta(minutes=30)},
                           application.config['SECRET_KEY'])

      return jsonify({'token' : token.decode('UTF-8')})

   return make_response('Could not verify',
                       401,
                       {'WWW-Authenticate' : 'Basic realm="Login required!"'})


@application.route('/home', methods=['GET'])
@token_required
def createGraph(current_user):
   transs = Transaction.query.filter_by(userId=current_user.id).all()

   dic = {}
   for trans in transs:
      temp = trans.amount
      print(temp)

      if not trans.income:
         temp = -1 * temp
         print(temp)


      if trans.category in dic.keys():
         dic[trans.category] = dic[trans.category] + temp
      else:
         print(temp)
         dic[trans.category] = temp

   fig = plt.figure()
   ax = fig.add_axes([0,0,1,1])
   ax.axis('equal')
   ax.pie(dic.values(), labels = dic.keys() ,autopct='%1.2f%%')
   fig.savefig('my_plot.png')

   return "<img src='my_plot.png'>"


@application.route('/home/<int:index>', methods=['GET'])
def changeMode():
   return "changeMode"


@application.route('/trans', methods=['POST'])
@token_required
def addTransaction(current_user):
   data = request.get_json()

   newTransaction = Transaction(amount=data['amount'],
                                income=data['income'],
                                date=datetime.utcnow(),
                                category=data['category'],
                                userId=current_user.id)

   db.session.add(newTransaction)
   db.session.commit()

   return jsonify({'message': "Transaction saved!"})


@application.route('/trans/<trans_id>', methods=['DELETE'])
@token_required
def removeTransaction(current_user, trans_id):
   trans = Transaction.query.filter_by(id=trans_id, userId=current_user.id).first()

   if not trans:
      return jsonify({'message': 'No transaction found!'})

   db.session.delete(trans)
   db.session.commit()

   return jsonify({'message': 'The transaction removed'})


@application.route('/trans/<trans_id>', methods=['GET'])
@token_required
def getOneTransaction(current_user, trans_id):
   trans = Transaction.query.filter_by(id=trans_id, userId=current_user.id).first()

   transactionData = {'amount': trans.amount}
   if not trans.income:
      transactionData['amount'] = -1 * transactionData['amount']
   transactionData['date'] = trans.date
   transactionData['category'] = trans.category

   return jsonify({'transaction': transactionData})


@application.route('/trans/', methods=['GET'])
@token_required
def getAllTransactions(current_user):
   transs = Transaction.query.filter_by(userId=current_user.id).all()

   output = []
   for trans in transs:
      transactionData = {'amount': trans.amount}
      if not trans.income:
         transactionData['amount'] = -1 * transactionData['amount']
      transactionData['date'] = trans.date
      transactionData['category'] = trans.category
      transactionData['ID'] = trans.id
      output.append(transactionData)

   return jsonify({'transactions': output})


if __name__ == '__main__':
   db.create_all()
   application.run(debug=True)

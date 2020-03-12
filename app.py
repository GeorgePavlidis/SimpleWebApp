import os
from flask import Flask, jsonify, request, redirect, make_response
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from matplotlib import pyplot as plt
from __init__ import User, Transaction, application, db
from middleware import token_required

# Graph mode
MODE = 4
# ==================================================================================================
# Entry Points
# ==================================================================================================
@application.route('/')
def index():
   """
   1. This function redirect the user to the home page
   """
   return redirect('/home')


@application.route('/user', methods=['POST'])
def createUser():
   """
   2. This function create new user and commit it to database
   """
   data = request.get_json()
   # Generate a hashed password using sha256
   hashedPass = generate_password_hash(data['password'], method='sha256')
   newUser = User(publicId=str(uuid.uuid4()),
                  username=data['username'],
                  password=hashedPass)
   # Commit new user
   db.session.add(newUser)
   db.session.commit()
   return jsonify({'message': 'New user created!'}), 201


@application.route('/user/<int:id>', methods=['GET'])
def getOneUser(id):
   """
   3. This function return publicID, username and password of specific user.
       NO Authorization is needed!
   """
   user = User.query.filter_by(id=id).first()
   userData = {
      'publicId': user.publicId,
      'username': user.username,
      'password': user.password,
   }
   return jsonify({'users': userData}), 200


@application.route('/user/', methods=['GET'])
def getAllUsers():
   """
   4. This function return ID, publicID, username and password of all users.
      NO Authorization is needed!
   """
   users = User.query.all()

   # Run through all users and collect the necessary information to display
   output = []
   for user in users:
      userData = {
         'ID': user.id,
         'publicId': user.publicId,
         'username': user.username,
         'password': user.password,
      }
      output.append(userData)

   return jsonify({'users': output}), 200


@application.route('/user/<int:id>', methods=['DELETE'])
@token_required
def deleteUser(currentUser, id):
   """
   5. This function deletes an user account, which means it deletes user and all its transactions.
      Any user have the authority to delete only its own user.
      Authorization is needed!
   """
   # If the account does not belong to current user
   if not currentUser.id == id:
      return jsonify({'message': "Fail to delete this user: Only the owner of this account can "
                                 "delete it!"}), 401

   # Delete User from User table and all rows from transaction table that belong to this user
   user = User.query.filter_by(id=id).first()
   Transaction.query.filter_by(userId=currentUser.id).delete()

   db.session.delete(user)
   db.session.commit()

   return jsonify({'message': 'The user deleted!'}), 200


@application.route('/login')
def login():
   """
   6. This function login a user and create a token for 30 minutes
   """
   auth = request.authorization
   # ===============================================================================================
   # 1. Check if both field is provided, username and password
   # ===============================================================================================
   if not auth or not auth.username or not auth.password:
      return make_response('Could not verify',
                           401,
                           {'WWW-Authenticate': 'Basic realm="Login required!"'})

   # ===============================================================================================
   # 2. Check if this user exist
   # ===============================================================================================
   user = User.query.filter_by(username=auth.username).first()
   if not user:
      return make_response('Could not verify',
                           401,
                           {'WWW-Authenticate': 'Basic realm="Login required!"'})

   # ===============================================================================================
   # 3. Check if the password is correct
   # ===============================================================================================
   if not check_password_hash(user.password, auth.password):
      return make_response('Could not verify',
                           401,
                           {'WWW-Authenticate': 'Basic realm="Login required!"'})

   # ===============================================================================================
   # 4. Generate token for this user for 30 minutes
   # ===============================================================================================
   token = jwt.encode({'publicId': user.publicId,
                       'exp': datetime.utcnow() + timedelta(minutes=30)},
                      application.config['SECRET_KEY'])
   # Return the token
   return jsonify({'token': token.decode('UTF-8')}), 200


@application.route('/home', methods=['GET'])
@token_required
def createGraph(currentUser):
   """
   7. This function returns a pie chart of sum of expenses per category
   """
   # Find all the transaction of current user
   transs = Transaction.query.filter_by(userId=currentUser.id).all()

   dic = {}
   for trans in transs:
      # Check if the transaction is income or expense
      # Keep only the expenses
      if trans.income:
         continue

      # Create a flag which indicate if the expense is in valid period
      inDateFlag = True
      if not application.config['MODE'] == 4:
         if application.config['MODE'] ==3:
            inDateFlag = datetime.utcnow().year == trans.date.year
         elif application.config['MODE']==2:
            inDateFlag = datetime.utcnow().year == trans.date.year \
                     and datetime.utcnow().month == trans.date.month
         elif application.config['MODE']==1:
            inDateFlag = datetime.utcnow().date() == trans.date.date()
      print(application.config['MODE'], inDateFlag)
      # Check if the transaction is in valid period of time 
      if not inDateFlag:
         continue

      # Add the amount of expense to its category in dictionary
      if trans.category in dic.keys():
         dic[trans.category] = dic[trans.category] + trans.amount
      else:
         dic[trans.category] = trans.amount

   # Create a pie chart for expenses
   fig = plt.figure()
   plt.pie(dic.values(), labels=dic.keys(), autopct='%1.2f%%')
   fig.savefig('my_plot.png')
   cwd = os.getcwd()
   return "<img src='"+ cwd +"/my_plot.png'>", 200


@application.route('/home/<int:index>', methods=['POST'])
def changeMode(index):
   """
   8. This function change the period of expenses that will be used of the pie
      MODE = 4 ==> OVERALL
      MODE = 3 ==> (YEAR, MONTH, DAY)
      MODE = 2 ==> (MONTH, DAY)
      MODE = 2 ==> (DAY)
   """
   application.config['MODE'] = index

   return "Mode Changed", 200


@application.route('/trans', methods=['POST'])
@token_required
def addTransaction(currentUser):
   """
   9. This function adds new transaction and commits it to database
   """
   data = request.get_json()
   newTransaction = Transaction(amount=data['amount'],
                                income=data['income'],
                                date=datetime.utcnow(),
                                category=data['category'],
                                userId=currentUser.id)
   # Commit new transaction 
   db.session.add(newTransaction)
   db.session.commit()

   return jsonify({'message': "Transaction saved!"}), 201


@application.route('/trans/<trans_id>', methods=['DELETE'])
@token_required
def removeTransaction(currentUser, trans_id):
   """
   10. This function removes a transaction from database
   """
   trans = Transaction.query.filter_by(id=trans_id, userId=currentUser.id).first()

   # Delete the transaction, if it exists 
   if not trans:
      return jsonify({'message': 'No transaction found!'})
   db.session.delete(trans)
   db.session.commit()

   return jsonify({'message': 'The transaction removed'}), 200


@application.route('/trans/<trans_id>', methods=['GET'])
@token_required
def getOneTransaction(currentUser, trans_id):
   """
   11. This function returns one specific transaction
   """
   trans = Transaction.query.filter_by(id=trans_id, userId=currentUser.id).first()
   # Collect necessary information for the transaction to display 
   transactionData = {'amount': trans.amount}
   if not trans.income:
      transactionData['amount'] = -1 * transactionData['amount']
   transactionData['date'] = trans.date
   transactionData['category'] = trans.category

   return jsonify({'transaction': transactionData}), 200


@application.route('/trans/', methods=['GET'])
@token_required
def getAllTransactions(currentUser):
   """
   12. This function returns all the transactions
   """
   transs = Transaction.query.filter_by(userId=currentUser.id).all()

   # Collect necessary information for each transaction to display 
   output = []
   for trans in transs:
      transactionData = {'amount': trans.amount}
      if not trans.income:
         transactionData['amount'] = -1 * transactionData['amount']
      transactionData['date'] = trans.date
      transactionData['category'] = trans.category
      transactionData['ID'] = trans.id
      output.append(transactionData)

   return jsonify({'transactions': output}), 200


if __name__ == '__main__':
   db.create_all()
   application.run(debug=True)

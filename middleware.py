from flask import jsonify, request, g
from functools import wraps
import jwt



def token_required(f):
   @wraps(f)
   def decorated(*args, **kwargs):
      """
      This decorator check if there is a token and if it is valid. If there are no token or it
      is not valid, the user can access the particular page
      """
      token = None

      # Check is there are token in request header
      if 'token' in request.headers:
         token = request.headers['token']
      else:
         return jsonify({'message': 'Token is missing!'}), 401

      try:
         # Decode the token using the secret key and check if the user exists in database
         data = jwt.decode(token, g.token)
         currentUser = User.query.filter_by(publicId=data['publicId']).first()
      except:
         return jsonify({'message': 'Token is invalid!'}), 401

      # Return the user found in token
      return f(currentUser, *args, **kwargs)

   return decorated
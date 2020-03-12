# SimpleWebApp
This is a Simple Server for a Money Manager App.

The application communicates with json, and it is suggested to use __Postman__ in order to use test this application  


__Functionality__

You can add a user and then add/remove your transactions in order to see a pie chart with your expenses 



__This application contains__:

- An SQLite database with two tables (Users, Transaction)
- A middleware function for authentication. This function checks if there is a token and if this token is valid 
- 11 Entry points:

    1. ```@application.route('/user', methods=['POST'])```:
      
      This function create new user and commit it to database


    2. ```@application.route('/user/<int:id>', methods=['GET'])```:
       
       This function return publicID, username and password of specific user.
           NO Authorization is needed!

    3. ```@application.route('/user/', methods=['GET'])```: 
         
         This function return ID, publicID, username and password of all users.
          NO Authorization is needed!

    4. ```@application.route('/login')```: 
         
         This function login a user and create a token for 30 minutes

    5. ```@application.route('/user', methods=['POST'])```: 
         
         This function create new user and commit it to database

    6. ```@application.route('/home', methods=['GET'])```: 
         
         This function returns a pie chart of sum of expenses per category

    7. ```@application.route('/home/<int:index>', methods=['POST'])```:
         
         This function change the period of expenses that will be used of the pie

          ```
          MODE = 4 ==> OVERALL
          MODE = 3 ==> (YEAR, MONTH, DAY)
          MODE = 2 ==> (MONTH, DAY)
          MODE = 2 ==> (DAY)
          ```

    8. ```@application.route('/trans', methods=['POST']))```: 
         
         This function adds new transaction and commits it to database

    9. ```@application.route('/trans/<trans_id>', methods=['DELETE'])```:
         
         This function removes a transaction from database

    10. ```@application.route('/trans/<trans_id>', methods=['GET'])```: 
           
           This function returns one specific transaction

    11. ```@application.route('/trans/', methods=['GET'])```: 
           
           This function returns all the transactions
           
           
## Dependencies 

```flask==v1.1.1```

```werkzeug==v1.0.0```

```jwt==v1.7.1```

```uuid==v0.1_1```

```matplotlib==v3.1.3```

```functools==v2.0```

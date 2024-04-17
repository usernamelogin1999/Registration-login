# from flask import Flask, request, render_template, redirect, session
# import mysql.connector
# import bcrypt

# app = Flask(__name__)
# app.secret_key = 'secret_key'

# def connect_to_database():
#     try:
#         mydb = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             passwd="mysql2002",
#             database="registrations",
#             auth_plugin='mysql_native_password'
#         )
#         return mydb
#     except mysql.connector.Error as error:
#         print("Error connecting to MySQL:", error)
#         return None

# def insert_row(mydb, name, email, password):
#     try:
#         mycursor = mydb.cursor()
#         sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
#         val = (name, email, password)
#         mycursor.execute(sql,val)
#         mydb.commit()
#         print("Row inserted successfully!")
#         mycursor.close()
#     except mysql.connector.Error as error:
#         print("Error inserting row:", error)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         # handle request
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']

#         # Hash the password
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

#         # Connect to the database
#         mydb = connect_to_database()
#         if not mydb:
#             return "Error connecting to database"

#         # Insert the row into the table
#         insert_row(mydb, name, email, hashed_password)

#         # Close database connection
#         mydb.close()

#         return redirect('/login')

#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         # Authenticate user - Add your authentication logic here
#         return redirect('/dashboard')

#     return render_template('login.html')

# @app.route('/dashboard')
# def dashboard():
#     if 'email' in session:
#         # Retrieve user information from the database based on the email stored in the session
#         email = session['email']
#         print(email)
#         mydb = connect_to_database()
#         if not mydb:
#             return "Error connecting to database"

#         mycursor = mydb.cursor()
#         sql = "SELECT * FROM users WHERE email = %s"  # Remove extra %s
#         val = (email,)  # Add comma to create a tuple
#         mycursor.execute(sql, val)
#         user = mycursor.fetchone()
#         print(user)
#         mydb.close()
#         print("User retrieved from database:", user) 
        
#         if user:
#             # Pass the user object to the template
#             return render_template('dashboard.html', user=user)
#         else:
#             # Handle the case where user information couldn't be retrieved
#             return "User not found"
#     else:
#         # Redirect to the login page if user is not logged in
#         return redirect('/login')

# @app.route('/logout')
# def logout():
#     # Logout user - Add your logout logic here
#     return redirect('/login')

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, request, render_template, redirect, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'secret_key'  # Replace with a strong secret key

def connect_to_database():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="mysql2002",  # Replace with your password
            database="registrations",
            auth_plugin='mysql_native_password'
        )
        return mydb
    except mysql.connector.Error as error:
        print("Error connecting to MySQL:", error)
        return None

def insert_row(mydb, name, email, password):
    try:
        mycursor = mydb.cursor()
        sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        val = (name, email, hashed_password)
        mycursor.execute(sql, val)
        mydb.commit()
        print("Row inserted successfully!")
        mycursor.close()
    except mysql.connector.Error as error:
        print("Error inserting row:", error)

def is_user_valid(email, password):
    mydb = connect_to_database()
    if not mydb:
        return False

    mycursor = mydb.cursor()
    sql = "SELECT * FROM users WHERE email = %s"
    val = (email,)
    mycursor.execute(sql, val)
    user = mycursor.fetchone()
    mydb.close()
    print(user)
    if user:
        return True
    else:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Connect to database and insert user
        mydb = connect_to_database()
        if not mydb:
            return "Error connecting to database"
        insert_row(mydb, name, email, hashed_password)
        mydb.close()

        return redirect('/login')  # Redirect to login after registration

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Authenticate user
        if is_user_valid(email, password):
            session['email'] = email
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        email = session['email']
        # ... (database connection and user retrieval code - adapt based on your needs)
        # You can display retrieved user information or a welcome message here
        return render_template('dashboard.html', user=user)  # Assuming user object exists
    else:
        return redirect('/login')  # Redirect to login if not logged in

@app.route('/logout')
def logout():
    # Logout user - Remove email from session or add your logout logic
    session.pop('email', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

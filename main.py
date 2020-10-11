from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import sys

app = Flask(__name__)
app.secret_key = 'prdel'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'vojta'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'iis'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        try:
            if session['loggedin']:
                return redirect(url_for('home'))
        except:
            return render_template('login.html', msg='')

    elif request.method == 'POST':
         # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['status'] = account['status']
            session['email'] = account['email']
            # Redirect to home page
            print('This is error output', file=sys.stderr)
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            return render_template('login.html', msg='Incorrect username/password!')
    # Show the login form with message (if any)

@app.route('/cant_login')        
def cant_login():
    return render_template("cant_login.html")

@app.route('/home/', methods=['GET', 'POST'])
def home():
    if session['status'] == "admin":
        return render_template('home.html', profile=session)
    elif session['status'] == "profesor":
        return render_template('home.html', profile=session)
    elif session['status'] == "assistent":
        return render_template('home.html', profile=session)
    elif session['status'] == "student":
        return render_template('home.html', profile=session)
    else:
        return render_template('login.html', msg='Please, log in')

@app.route('/home/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/home/add_user')
def add_user():
    if session['status'] != 'admin':
        return redirect(url_for('home'))
    
    return render_template('add_user.html')



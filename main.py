from flask import Flask, render_template, request, redirect, url_for, session, flash
#from flask_mysqldb import MySQL
from forms import AddUserForm, ChangeEmailForm, ChangeNameForm, ChangePasswordForm
#import MySQLdb.cursors
import re
import secrets
import sys
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'prdel'

#SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/flaskcodeloop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'wulferion'
app.config['MYSQL_PASSWORD'] = 'prdel'
app.config['MYSQL_DB'] = 'iis'

# Intialize MySQL
#mysql = MySQL(app)

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


        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))


        # Fetch one record and return result


        #account = cursor.fetchone()

        
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
    if session['loggedin']:
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

@app.route('/create_test')
def create_test():
    return render_template('create_test.html', profile =session)

@app.route('/home/add_user', methods=['GET','POST'])
def add_user():
    if session['status'] != 'admin':
        return redirect(url_for('home'))
    
    form = AddUserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            password = secrets.token_hex(8)
            flash(f'Login information for {form.name.data} {form.surname.data} are:\nEmail: {form.email.data}\nPassword: {password}', 'success')
            return redirect(url_for('home'))
        else:
            flash('prdel', 'danger')
            return redirect(url_for('add_user'))


    return render_template('add_user.html', form=form, profile=session)

@app.route('/home/settings')
def settings():
    return render_template('settings.html', profile=session)

@app.route('/home/settings/change_name')
def changeName():
    form = ChangeNameForm()
    return render_template('change_name.html', profile=session, form=form)

@app.route('/home/settings/change_password')
def changePassword():
    form = ChangePasswordForm()
    return render_template('change_password.html', profile=session, form=form)

@app.route('/home/settings/change_email')
def changeEmail():
    form = ChangeEmailForm()
    return render_template('change_email.html', profile=session, form=form)

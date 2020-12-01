from flask import Flask, render_template, request, redirect, url_for, session, flash
#from flask_mysqldb import MySQL
from forms import AddUserForm, ChangeEmailForm, ChangeNameForm, ChangePasswordForm
#import MySQLdb.cursors
import re
import secrets
import sys
import sqlalchemy as sq
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session,sessionmaker, Session


app = Flask(__name__)
app.secret_key = 'prdel'

#SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:VelkaPrdel@localhost/iis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = sq.create_engine('mysql+pymysql://root:VelkaPrdel@localhost/iis')
db=scoped_session(sessionmaker(bind=engine))
metadata = sq.MetaData()
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
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        account = db.execute("SELECT * FROM accounts WHERE email=:email",{"email":email}).fetchone()
        
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            if password == account['password']:
                session['loggedin'] = True
                session['id'] = account['id']
                session['name'] = account['name']
                session['surname'] = account['surname']
                session['status'] = account['status']
                session['email'] = account['email']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                return render_template('login.html', msg='Incorrect password!')

        else:
            # Account doesnt exist or username/password incorrect
            return render_template('login.html', msg='Incorrect email/password!')
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

@app.route('/home/add_user', methods=['GET','POST'])
def add_user():
    if session['status'] != 'admin':
        return redirect(url_for('home'))

    form = AddUserForm(request.form)
    if request.method == "POST":
        if form.validate():
            if None == db.execute("SELECT * FROM accounts WHERE email=:email",{"email":form.email.data}).fetchone():
                password = secrets.token_hex(4)
                data = {"password":password, "name":form.name.data,"surname":form.surname.data,"email":form.email.data, "status":form.status.data}
                db.execute(f"INSERT INTO `accounts` (`password`, `name`, `surname`, `email`, `status`) VALUES (:password, :name, :surname, :email,:status)", data)
                db.commit()
                flash(f'Login information for {form.name.data} {form.surname.data} are:\nEmail: {form.email.data}\nPassword: {password}', 'success')
                return redirect(url_for('home'))
            else:
                flash("Email is already used", 'danger')
                return redirect(url_for('add_user'))   
        else:
            flash("not valid values", 'danger')
            return redirect(url_for('add_user'))


    return render_template('add_user.html', form=form, profile=session)

@app.route('/home/settings')
def settings():
    return render_template('settings.html', profile=session)

@app.route('/home/settings/change_name', methods=['GET','POST'])
def changeName():
    form = ChangeNameForm(request.form)
    if request.method == "POST":
        if not form.validate():
            flash("something went wrong", 'danger')
        db.execute(f"""update `accounts` 
                    set `surname`='{form.surname.data}',
                    set `name`='{form.name.data}'
                    where id = {session['id']}""")
        db.commit()        
        flash('surname changed!', 'success')
        return render_template('change_email.html', profile=session, form=form)
    return render_template('change_name.html', profile=session, form=form)

@app.route('/home/settings/change_password', methods=['GET','POST'])
def changePassword():
    form = ChangePasswordForm(request.form)
    if request.method == "POST":
        if not form.validate():
            flash("something went wrong", 'danger')
        db.execute(f"""update `accounts` 
                    set `password`='{form.password.data}'
                    where id = {session['id']}""")
        db.commit()        
        flash('Password changed!', 'succes')
        return render_template('change_password.html', profile=session, form=form)

    else:
        return render_template('change_password.html', profile=session, form=form)

@app.route('/home/settings/change_email', methods=['GET','POST'])
def changeEmail():
    form = ChangeEmailForm(request.form)
    if request.method == "GET":
        return render_template('change_email.html', profile=session, form=form)

    if request.method == "POST":
        if not form.validate():
            flash("something went wrong", 'danger')
        if None == db.execute("SELECT * FROM accounts WHERE email=:email",{"email":form.email.data}).fetchone():
            db.execute(f"""update `accounts` 
                        set `email`='{form.email.data}'
                        where id = {session['id']}""")
            db.commit()        
            flash('email changed!', 'success')
            return render_template('change_email.html', profile=session, form=form)
    flash("something went wrong", 'danger')
    return render_template('change_email.html', profile=session, form=form)

@app.route('/home/manage_users', methods=['GET','POST'])
def manage_users():
    if session['status'] != 'admin':
        flash("Acces denied", 'danger')
        return redirect(url_for('home'))

    table = db.execute("select * from accounts")

    return render_template('manage_users.html', profile=session, users=table)

@app.route('/home/remove_user/<string:id>')
def remove_user(id):
    flash(id)
    print(db.execute("SELECT * FROM accounts WHERE id=:id",{"id":id}).fetchone(), file=sys.stderr)
    #print(db.execute(f'select * from accounts where id={id})'))
    return render_template('remove_user.html', profile=session)

@app.route('/home/change_user/<string:id>')
def change_user(id):
    flash(id)
    print(db.execute("SELECT * FROM accounts WHERE id=:id",{"id":id}).fetchone(), file=sys.stderr)
    #print(db.execute(f'select * from accounts where id={id})'))
    return render_template('change_user.html', profile=session)
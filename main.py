from flask import Flask, render_template, request, redirect, url_for, session, flash
#from flask_mysqldb import MySQL
from forms import *
#import MySQLdb.cursors
import re
import secrets
import sys
import os
import json
import datetime
import sqlalchemy as sq
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session,sessionmaker, Session


app = Flask(__name__)
app.secret_key = 'prdel'

#SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:prdel@localhost/iis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = sq.create_engine('mysql+pymysql://root:prdel@localhost/iis')
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

@app.route('/create_test', methods=['GET','POST'])
def create_test():
    #Add forms
    configform = TestConfigForm(request.form)
    fullform = FullTextQuestionForm(request.form)
    numform = NumQuestionForm(request.form)
    abcfrom = AbcQuestionForm(request.form)
    #Check for active session
    if 'test_config' in session:
        config = session['test_config']
    else:
        config = {"name": "",
                  "start": "01/01/1111",
                  "end": "01/01/1111",
                  "question_num": "1"
                }
    if 'questions' in session:
        questions = session['questions']
    else:
        questions = list()

    if request.method == "POST":
        #Continue depending on the button used
        #create test
        if 'create' in request.form:
            if request.form['create'] == 'Create test':
                #save config to session
                config['name'] = configform.name.data
                config['start'] = configform.start_date.data.strftime("%m/%d/%Y")
                config['end'] = configform.end_date.data.strftime("%m/%d/%Y")
                config['question_num'] = configform.question_num.data
                session['test_config'] = config
            #Question creation buttons
            elif request.form['create'] == 'Create full question':
                question = dict()
                question['id'] = questions.__len__()
                question['type'] = "full"
                question['question'] = fullform.question.data
                question['value'] = fullform.value.data
                questions.append(question)
                session['questions'] = questions
            elif request.form['create'] == 'Create number question':
                question = dict()
                question['id'] = questions.__len__()
                question['type'] = "number"
                question['question'] = numform.question.data
                question['value'] = numform.value.data
                question['answer'] = numform.answer.data
                questions.append(question)
                session['questions'] = questions
            elif request.form['create'] == 'Create abcd question':
                question = dict()
                question['id'] = questions.__len__()
                question['type'] = "abcd"
                question['question'] = abcfrom.question.data
                question['value'] = abcfrom.value.data
                question['a'] = abcfrom.a.data
                question['b'] = abcfrom.b.data
                question['c'] = abcfrom.c.data
                question['d'] = abcfrom.d.data
                question['answer'] = abcfrom.answer.data
                questions.append(question)
                session['questions'] = questions
        #Remove question
        if 'remove' in request.form:          
            for question in questions:
                if question['id'] == int(request.form['remove']):
                    questions.remove(question)
                    session['questions'] = questions
                    break
        #Update test
        if 'update' in request.form:
            if request.form['update'] == 'Update test':
                #save config to session
                config['name'] = configform.name.data
                config['start'] = configform.start_date.data.strftime("%m/%d/%Y")
                config['end'] = configform.end_date.data.strftime("%m/%d/%Y")
                config['question_num'] = configform.question_num.data
                session['test_config'] = config
        #Save test
        if 'save' in request.form:
            if request.form['save'] == 'Save test':
                config['name'] = configform.name.data
                config['start'] = configform.start_date.data.strftime("%m/%d/%Y")
                config['end'] = configform.end_date.data.strftime("%m/%d/%Y")
                config['question_num'] = configform.question_num.data
                #validate forms
                if configform.start_date.validate(request.form) and configform.end_date.validate(request.form) and configform.question_num.validate(request.form):
                    start = datetime.datetime.strptime(config['start'], '%m/%d/%Y')
                    start = start.strftime("%Y-%m-%d")
                    end = datetime.datetime.strptime(config['end'], '%m/%d/%Y')
                    end = end.strftime("%Y-%m-%d")
                    #save to DB
                    db.execute(f"INSERT INTO `test_template` (`active_from`, `active_to`, `creator`) VALUES ('{start}','{end}','{session['id']}')")
                    tid = db.execute("SELECT test_id FROM test_template ORDER BY test_id DESC LIMIT 1").fetchone()
                    #save JSON
                    test = dict()
                    config['id'] = tid[0]
                    test['config'] = config
                    test['questions'] = questions
                    with open(f"test_templates/test_template{tid[0]}.json","w") as testfile:
                        json.dump(test,testfile)
                    db.execute(f"UPDATE `test_template` SET `file`='test_templates/test_template{tid[0]}.json' WHERE test_id = {tid[0]}")
                    db.commit()
                    #pop all from session
                    session.pop('test_config',None)
                    session.pop('questions',None)
                    config = {"name": "",
                        "start": "01/01/1111",
                        "end": "01/01/1111",
                        "question_num": "1"
                        }
                #return to previous state TODO: feedback flash
        #Cancel
        if configform.cancel.data:
            #pop all data from session
            session.pop('test_config',None)
            session.pop('questions',None)
            config = {"name": "",
                  "start": "01/01/1111",
                  "end": "01/01/1111",
                  "question_num": "1" 
                }
        if configform.add_full.data:
            return render_template('create_full.html',profile=session,form=fullform)
        if configform.add_num.data:
            return render_template('create_num.html',profile=session,form=numform)
        if configform.add_abc.data:
            return render_template('create_abcd.html',profile=session,form=abcfrom)

    
    #prefill the forms back 
    print(f"config: {config}",file=sys.stderr)
    if 'test_config' in session:
        print(f"session: {session['test_config']}",file=sys.stderr) 

    start_time_obj = datetime.datetime.strptime(config['start'], '%m/%d/%Y')
    end_time_obj = datetime.datetime.strptime(config['end'], '%m/%d/%Y')
    configform.name.data = config['name']
    configform.start_date.data = start_time_obj
    configform.end_date.data = end_time_obj
    configform.question_num.data = config['question_num']
    return render_template('create_test.html', profile=session, config=configform, questions=questions)
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

@app.route("/home/my_tests",methods=['GET','POST'])
def my_tests():
    #Get user ID
    user_id = session['id']
    #Querry DB
    result = db.execute(f"SELECT `file` FROM `test_template` WHERE `creator` = {user_id}")
    test_files = [row[0] for row in result] 
    #Print for all results in template
    tests = list()
    for test_file in test_files:
        with open(test_file,"r") as f:
            tests.append(json.load(f))

    if request.method == "POST":
        #Edit tests
        if 'edit' in request.form:
            for test in tests:
                if test['config']['id'] == int(request.form['edit']):
                    #Fill session
                    session['test_config'] = test['config']
                    session['questions'] = test['questions']
                    return redirect(url_for('create_test'))
        if 'remove' in request.form:
            for test in tests:
                if test['config']['id'] == int(request.form['remove']):
                    db.execute(f"DELETE FROM `test_template` WHERE `test_id` = {test['config']['id']}")
                    db.commit()
                    os.remove(f"test_templates/test_template{test['config']['id']}.json")
                    tests.remove(test)
    return render_template('my_tests.html', profile=session, tests=tests)
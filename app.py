from flask import Flask, render_template, request, redirect, url_for, session, flash
#from flask_mysqldb import MySQL
from forms import *
#import MySQLdb.cursors
import re
import sys
import os
import json
import datetime
import sqlalchemy as sq
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session,sessionmaker, Session


app = Flask(__name__)
app.secret_key = 'secretkey'

#SqlAlchemy Database Configuration With Mysql

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://xkrejc68@real-iis:prdel666$@real-iis.mysql.database.azure.com/iis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = sq.create_engine('mysql+pymysql://xkrejc68@real-iis:prdel666$@real-iis.mysql.database.azure.com/iis', pool_pre_ping=True)
dbSession = sessionmaker(bind=engine, expire_on_commit=False)
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
        db = dbSession()
        account = db.execute("SELECT * FROM accounts WHERE email=:email",{"email":email}).fetchone()
        db.close()
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
            db = dbSession()
            if None == db.execute("SELECT * FROM accounts WHERE email=:email",{"email":form.email.data}).fetchone():
                password = 'heslo'
                data = {"password":password, "name":form.name.data,"surname":form.surname.data,"email":form.email.data, "status":form.status.data}
                db.execute(f"INSERT INTO `accounts` (`password`, `name`, `surname`, `email`, `status`) VALUES (:password, :name, :surname, :email,:status)", data)
                db.commit()
                db.close()
                flash(f'Login information for {form.name.data} {form.surname.data} are:\nEmail: {form.email.data}\nPassword: {password}', 'success')
                return redirect(url_for('home'))
            else:
                db.close()
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
                
                
        db = dbSession()
        db.execute(f"""update `accounts` 
                    set `surname`='{form.surname.data}',
                    set `name`='{form.name.data}'
                    where id = {session['id']}""")
        db.commit()  
        db.close()      
        flash('surname changed!', 'success')
        return render_template('change_email.html', profile=session, form=form)
    return render_template('change_name.html', profile=session, form=form)

@app.route('/home/settings/change_password', methods=['GET','POST'])
def changePassword():
    form = ChangePasswordForm(request.form)
    if request.method == "POST":
        if not form.validate():
            flash("something went wrong", 'danger')
        
        db = dbSession()
        db.execute(f"""update `accounts` 
                    set `password`='{form.password.data}'
                    where id = {session['id']}""")
        db.commit()        
        db.close()
        flash('Password changed!', 'success')
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
                
        db = dbSession()
        if None == db.execute("SELECT * FROM accounts WHERE email=:email",{"email":form.email.data}).fetchone():
            db.execute(f"""update `accounts` 
                        set `email`='{form.email.data}'
                        where id = {session['id']}""")
            db.commit()   
            db.close()     
            flash('email changed!', 'success')
            return render_template('change_email.html', profile=session, form=form)
        db.close()
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
                question['earned'] = 0
                question['stud_answer'] = ""
                questions.append(question)
                session['questions'] = questions
            elif request.form['create'] == 'Create number question':
                question = dict()
                question['id'] = questions.__len__()
                question['type'] = "number"
                question['question'] = numform.question.data
                question['value'] = numform.value.data
                question['answer'] = numform.answer.data
                question['earned'] = 0
                question['stud_answer'] = ""
                questions.append(question)
                session['questions'] = questions
            elif request.form['create'] == 'Create abcd question':
                question = dict()
                question['id'] = questions.__len__()
                question['type'] = "abcd"
                question['question'] = abcfrom.question.data
                question['value'] = abcfrom.value.data
                question['earned'] = 0
                question['a'] = abcfrom.a.data
                question['b'] = abcfrom.b.data
                question['c'] = abcfrom.c.data
                question['d'] = abcfrom.d.data
                question['answer'] = abcfrom.answer.data
                question['stud_answer'] = ""
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
                    db = dbSession()
                    if not 'edit' in session:
                        db.execute(f"INSERT INTO `test_template` (`active_from`, `active_to`, `creator`) VALUES ('{start}','{end}','{session['id']}')")
                        tid = db.execute("SELECT test_id FROM test_template ORDER BY test_id DESC LIMIT 1").fetchone()
                    #update DB (editing from another page)
                    else:
                        tid = (session['test_config']['id'],None)
                        db.execute(f"UPDATE `test_template` SET `active_from`='{start}',`active_to`='{end}' WHERE test_id = {tid[0]}")

                    #save JSON
                    test = dict()
                    config['id'] = tid[0]
                    test['config'] = config
                    test['questions'] = questions
                    with open(f"test_templates/test_template{tid[0]}.json","w") as testfile:
                        json.dump(test,testfile)
                    db.execute(f"UPDATE `test_template` SET `file`='test_templates/test_template{tid[0]}.json' WHERE test_id = {tid[0]}")
                    db.commit()
                    db.close()
                    #pop all from session
                    session.pop('test_config',None)
                    session.pop('questions',None)
                    session.pop('edit',None)
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
            session.pop('edit',None)
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
    db = dbSession()
    table = db.execute("select * from accounts")
    db.close()
    return render_template('manage_users.html', profile=session, users=table)

@app.route('/home/remove_user/<string:id>')
def remove_user(id):
    print(id, session['id'], file = sys.stderr)
    if int(id) == int(session['id']):
        print("i am inside", file = sys.stderr)
        flash("You cant remove yourself", 'danger')
        return redirect(url_for('manage_users'))
    else:
        flash("User removed", 'success')
        db = dbSession()
        db.execute("DELETE FROM accounts WHERE id=:id",{"id":id})
        db.commit()
        db.close()
        return redirect(url_for('manage_users'))

@app.route('/home/change_user/<string:id>', methods=['GET','POST'])
def change_user(id):
    db = dbSession()
    form = ChangeUserDataForm(request.form)
    user = db.execute("SELECT * FROM accounts WHERE id=:id",{"id":id}).fetchone()
    if request.method == "GET":
        form.password.data = user[1]
        form.confirm_password.data = user[1]
        form.name.data = user[2]
        form.surname.data = user[3]
        form.email.data = user[4]
        form.status.data = user[5]
        db.close()    
        return render_template('change_user.html', profile=session, form=form)
    if request.method == "POST":
        if not form.validate():
            flash("something went wrong", 'danger')
            return render_template('change_user.html', profile=session, form=form)
        if form.password.data == '':
            password = user[1]
        else:
             password = form.password.data
        
        db.execute(f"""update `accounts` 
                    set 
                    `password`='{password}',
                    `name`='{form.name.data}',
                    `surname`='{form.surname.data}',
                    `email`='{form.email.data}',
                    `status`='{form.status.data}'
                    where id = {id};""")
        db.commit()    
        db.close()    
        flash('User changed!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('change_user.html', profile=session, form=form)

@app.route("/home/my_tests",methods=['GET','POST'])
def my_tests():
    #Get user ID
    user_id = session['id']
    #Querry DB
    db = dbSession()
    result = db.execute(f"SELECT `file` FROM `test_template` WHERE `creator` = {user_id}")
    ass_result = db.execute(f"SELECT `registrations`.`test_id`,`name`,`surname`,`id` FROM `accounts` INNER JOIN `registrations` ON `accounts`.`id` = `registrations`.`person_id` INNER JOIN `test_template` ON `registrations`.`test_id` = `test_template`.`test_id` WHERE `creator` = '{user_id}' AND `person_type` = 'assistant' AND `approved` = '1'")
    db.close()
    test_files = [row[0] for row in result] 
    #Print for all results in template
    tests = list()
    for test_file in test_files:
        with open(test_file,"r") as f:
            tests.append(json.load(f))

    #approved assistants for print
    assistants = list()
    for row in ass_result:
        assistant = {'test': row[0],'name': row[1],'surname': row[2],'id': row[3]}
        assistants.append(assistant)

    if request.method == "POST":
        #Edit tests
        if 'edit' in request.form:
            for test in tests:
                if test['config']['id'] == int(request.form['edit']):
                    #Fill session
                    session['test_config'] = test['config']
                    session['questions'] = test['questions']
                    session['edit'] = 1
                    return redirect(url_for('create_test'))
        if 'remove' in request.form:
            for test in tests:
                if test['config']['id'] == int(request.form['remove']):
                    db = dbSession()
                    #Find all students with active tests
                    result = db.execute(f"SELECT `test_copy` from `registrations` WHERE `test_id` = {test['config']['id']} AND `test_copy` IS NOT NULL")
                    for row in result:
                        os.remove(row[0])
                    db.execute(f"DELETE FROM `registrations` WHERE `test_id` = {test['config']['id']}")
                    db.execute(f"DELETE FROM `test_template` WHERE `test_id` = {test['config']['id']}")
                    db.commit()
                    db.close()
                    os.remove(f"test_templates/test_template{test['config']['id']}.json")
                    tests.remove(test)
        if 'activate' in request.form:
            for test in tests:
                if test['config']['id'] == int(request.form['activate']):
                    db = dbSession()
                    result = db.execute(f"SELECT `person_id` FROM `registrations` WHERE `test_id` = {test['config']['id']} AND `person_type` = 'student' AND `approved` = '1'")
                    sudents =[row[0] for row in result]
                    test['score'] = 'NEHODNOCENO'
                    for student in sudents:
                        with open(f"test_students/test_{student}_{test['config']['id']}.json","w") as f:
                            json.dump(test,f)
                        db.execute(f"UPDATE `registrations` SET `test_copy` = 'test_students/test_{student}_{test['config']['id']}.json' WHERE `test_id` = '{test['config']['id']}' AND `person_id` = '{student}' AND `person_type` = 'student'")
                        db.commit()
                    db.close()

    return render_template('my_tests.html', profile=session, tests=tests, assistants = assistants)

@app.route("/home/apply",methods=['GET','POST'])
def assistant_apply():
    user_id = session['id']
    #Querry DB
    db = dbSession()
    result = db.execute(f"SELECT `file` FROM `test_template`")
    test_files = [row[0] for row in result]
    #Get info on tests
    tests = list()
    for test_file in test_files:
        with open(test_file,"r") as f:
            tests.append(json.load(f))
    result = db.execute(f"SELECT `test_id` FROM `registrations` WHERE `person_id` = '{user_id}' AND `person_type` = 'assistant'")
    applied = [row[0] for row in result]
    result = db.execute(f"SELECT `test_id` FROM `registrations` WHERE `person_id` = '{user_id}' AND `person_type` = 'assistant' AND `approved`='1'")
    approved = [row[0] for row in result]
    if request.method == "POST":
        #Apply tests
        if 'apply' in request.form:
            for test in tests:
              if test['config']['id'] == int(request.form['apply']):
                  #input into DB
                  db.execute(f"INSERT INTO `registrations` (`person_id`, `person_type`, `test_id` ,`approved`,`score`) VALUES ('{user_id}','assistant','{test['config']['id']}','0','0')")
                  db.commit()
                  applied.append(test['config']['id'])
        #Unnaply from tests
        if 'unapply' in request.form:
            for test in tests:
              if test['config']['id'] == int(request.form['unapply']):
                  #input into DB
                  db.execute(f"DELETE FROM `registrations` WHERE `person_id` = '{user_id}' and `test_id` = '{test['config']['id']}' and `person_type`='assistant'")
                  db.commit()
                  applied.remove(test['config']['id'])
    db.close()         
    return render_template('assistant_apply.html', profile=session, tests=tests, applied=applied, approved=approved)

@app.route("/home/register",methods=['GET','POST'])
def student_register():
    user_id = session['id']
    #Querry DB
    db = dbSession()
    result = db.execute(f"SELECT `file` FROM `test_template`")
    test_files = [row[0] for row in result]
    #Get info on tests
    tests = list()
    for test_file in test_files:
        with open(test_file,"r") as f:
            tests.append(json.load(f))
    result = db.execute(f"SELECT `test_id` FROM `registrations` WHERE `person_id` = '{user_id}' AND `person_type` = 'student'")
    applied = [row[0] for row in result]
    result = db.execute(f"SELECT `test_id` FROM `registrations` WHERE `person_id` = '{user_id}' AND `person_type` = 'student' AND `approved`='1'")
    approved = [row[0] for row in result]
    if request.method == "POST":
        #Apply tests
        if 'apply' in request.form:
            for test in tests:
              if test['config']['id'] == int(request.form['apply']):
                  #input into DB
                  db.execute(f"INSERT INTO `registrations` (`person_id`, `person_type`, `test_id` ,`approved`,`score`) VALUES ('{user_id}','student','{test['config']['id']}','0','0')")
                  db.commit()
                  applied.append(test['config']['id'])
        #Unnaply from tests
        if 'unapply' in request.form:
            for test in tests:
              if test['config']['id'] == int(request.form['unapply']):
                  result = db.execute(f"SELECT `test_copy` FROM `registrations` WHERE `person_id` = '{user_id}' and `test_id` = '{test['config']['id']}' and `person_type`='student' and `test_copy` is not null")
                  for row in result:
                        os.remove(row[0])
                  #input into DB
                  db.execute(f"DELETE FROM `registrations` WHERE `person_id` = '{user_id}' and `test_id` = '{test['config']['id']}' and `person_type`='student'")
                  db.commit()
                  applied.remove(test['config']['id'])
                  if test['config']['id'] in approved:
                    approved.remove(test['config']['id'])
    db.close()              
    return render_template('student_register.html', profile=session, tests=tests, applied=applied, approved=approved)

@app.route("/home/approveass",methods=['GET','POST'])
def approve_assistant():
    user_id = session['id']
    #Querry DB
    db = dbSession()
    result = db.execute(f"SELECT `id`,`name`,`surname`,`file` FROM `accounts` INNER JOIN `registrations` ON `accounts`.`id` = `registrations`.`person_id` INNER JOIN `test_template` ON `registrations`.`test_id` = `test_template`.`test_id` WHERE `creator` = '{user_id}' AND `person_type` = 'assistant' AND `approved` = '0'")
    assistants = list()
    for row in result:
        assistant = dict()
        assistant['id'] = row[0]
        assistant['name'] = row[1]
        assistant['surname'] = row[2]
        with open(row[3],"r") as f:
            assistant['test'] = json.load(f)
        assistants.append(assistant)

    if request.method == "POST":
        #Approve
        if 'approve' in request.form:
            for assistant in assistants:
              if assistant['test']['config']['id'] == int(request.form['approve']):
                  #input into DB
                  db.execute(f"UPDATE `registrations` SET `approved` = '1' WHERE `person_id`={assistant['id']} and `test_id` = {assistant['test']['config']['id']}")
                  db.commit()
                  assistants.remove(assistant)
        #Deny
        if 'deny' in request.form:
            for assistant in assistants:
              if assistant['test']['config']['id'] == int(request.form['deny']):
                  #input into DB
                  db.execute(f"DELETE FROM `registrations` WHERE `person_id` = {assistant['id']} AND `test_id` = {assistant['test']['config']['id']}")
                  db.commit()
                  assistants.remove(assistant)
    db.close()
    return render_template('approve_assistant.html', profile=session, assistants=assistants)

@app.route("/home/approvestud",methods=['GET','POST'])
def approve_student():
    user_id = session['id']
    #Querry DB
    db = dbSession()
    result = db.execute(f"SELECT `id`,`name`,`surname`,`file` FROM `accounts` INNER JOIN `registrations` ON `accounts`.`id` = `registrations`.`person_id` INNER JOIN `test_template` ON `registrations`.`test_id` = `test_template`.`test_id` WHERE `person_type` = 'student' AND `approved` = '0'")
    assistants = list()
    for row in result:
        assistant = dict()
        assistant['id'] = row[0]
        assistant['name'] = row[1]
        assistant['surname'] = row[2]
        with open(row[3],"r") as f:
            assistant['test'] = json.load(f)
        assistants.append(assistant)

    if request.method == "POST":
        #Approve
        if 'approve' in request.form:
            for assistant in assistants:
              if assistant['test']['config']['id'] == int(request.form['approve']):
                  #input into DB
                  db.execute(f"UPDATE `registrations` SET `approved` = '1' WHERE `person_id`={assistant['id']} and `test_id` = {assistant['test']['config']['id']}")
                  db.commit()
                  assistants.remove(assistant)
        #Deny
        if 'deny' in request.form:
            for assistant in assistants:
              if assistant['test']['config']['id'] == int(request.form['deny']):
                  #input into DB
                  db.execute(f"DELETE FROM `registrations` WHERE `person_id` = {assistant['id']} AND `test_id` = {assistant['test']['config']['id']}")
                  db.commit()
                  assistants.remove(assistant)
    db.close()
    return render_template('approve_student.html', profile=session, students=assistants)

@app.route("/home/active_tests",methods=['GET','POST'])
def active_tests():
    #Get user ID
    user_id = session['id']
    #Querry DB
    db = dbSession()
    result = db.execute(f"SELECT `test_copy` FROM `registrations` WHERE `person_id` = '{user_id}' AND `approved` = '1' AND `test_copy` is not NULL")
    test_files = [row[0] for row in result] 
    #Print for all results in template
    tests = list()
    for test_file in test_files:
        with open(test_file,"r") as f:
            tests.append(json.load(f))
   
    cur_date = datetime.date.today()
    for test in tests:
        start_time_obj = datetime.datetime.strptime(test['config']['start'], '%m/%d/%Y')
        end_time_obj = datetime.datetime.strptime(test['config']['end'], '%m/%d/%Y')
        #Too soon or too late -> ignore
        if (start_time_obj.date() > cur_date) or (end_time_obj.date() < cur_date):
            tests.remove(test)
            continue
    db.close()
    if request.method == "POST":
        if 'open' in request.form:
          for test in tests:
              if test['config']['id'] == int(request.form['open']):
                  return redirect(url_for('test',test_id = test['config']['id']))
        
    return render_template('active_tests.html', profile=session, tests=tests)

@app.route("/home/test/<string:test_id>",methods=['GET','POST'])
def test(test_id):
    user_id = session['id']
    answerform = AnwerForm(request.form)
    #open test file and load test into memory
    with open(f"test_students/test_{user_id}_{test_id}.json","r") as f:
        test = json.load(f)

    if request.method == "POST":
        if answerform.save.data:
            qid = int(request.form['question_id']) 
            if test['questions'][qid]['type'] == 'full':
                test['questions'][qid]['stud_answer'] = answerform.answer.data
            elif test['questions'][qid]['type'] == 'number':
                answerform.answer_num.validate(request.form)
                test['questions'][qid]['stud_answer'] = answerform.answer_num.data
            else:
                test['questions'][qid]['stud_answer'] = answerform.answer_abc.data
            with open(f"test_students/test_{user_id}_{test_id}.json","w") as f:
                json.dump(test,f)

    return render_template('test.html', profile=session, test=test, answer = answerform)

@app.route("/home/my_tests/",methods=['GET','POST'])
def kick_ass():
    db = dbSession()
    db.execute(f"DELETE FROM `registrations` WHERE `person_id` = '{request.args.get('assistant_id')}' AND `test_id` = {request.args.get('test_id')} AND `person_type` = 'assistant'")
    db.commit()
    db.close()
    return redirect(url_for('my_tests'))

@app.route("/home/score",methods=['GET','POST'])
def score_tests():
    #Get user ID
    user_id = session['id']
    #Querry DB
    db = dbSession()
    tests = list()
    #Get all test where user is assistent
    result = db.execute(f"SELECT `test_id` FROM `registrations` WHERE `person_id` = '{user_id}' AND `approved` = '1' AND `person_type` = 'assistant'")
    my_tests = [row[0] for row in result]
    #Get all tests where user is creator
    result = db.execute(f"SELECT `test_id` FROM `test_template` WHERE `creator` = '{user_id}'")
    for row in result:
        if row[0] in my_tests:
            continue
        my_tests.append(row[0])

    for test in my_tests:
        result = db.execute(f"SELECT `test_copy`,`person_id`,`name`,`surname` FROM `registrations` INNER JOIN `accounts` ON `accounts`.`id` = `registrations`.`person_id` WHERE `person_type` = 'student' AND `approved` = '1' AND `test_copy` is not NULL and `test_id` = '{test}'")
        for row in result:
            with open(row[0],"r") as f:
                test = json.load(f)
                test['student'] = {'id': row[1],'name': row[2],'surname': row[3]}
                tests.append(test)
            
    db.close()

    cur_date = datetime.date.today()
    for test in tests:
        end_time_obj = datetime.datetime.strptime(test['config']['end'], '%m/%d/%Y')
        #only interested in done tests
        if (end_time_obj.date() > cur_date): 
            tests.remove(test)
            continue

    if request.method == "POST":
        if 'open' in request.form:
          for test in tests:
              if test['config']['id'] == int(request.form['open']):
                  return redirect(url_for('score_test',test_id = test['config']['id'],student_id = test['student']['id']))

    return render_template("score_tests.html", profile=session, tests=tests)

@app.route("/home/score_test/",methods=['GET','POST'])
def score_test():
    scoreform = AnwerForm(request.form)
    #open test file and load test into memory
    with open(f"test_students/test_{request.args.get('student_id')}_{request.args.get('test_id')}.json","r") as f:
        test = json.load(f)

    if request.method == "POST":
        if scoreform.save.data:
            qid = int(request.form['question_id']) 
            scoreform.answer_num.validate(request.form)
            if(test['questions'][qid]['value'] < scoreform.answer_num.data or scoreform.answer_num.data < 0):
                flash(f"Out of range for points max is: {test['questions'][qid]['value']}",'danger')
                return render_template('score_test.html', profile=session, test=test, answer = scoreform)

            test['questions'][qid]['earned'] = scoreform.answer_num.data
            test['score'] = int(test['score']) + int(scoreform.answer_num.data)
            with open(f"test_students/test_{request.args.get('student_id')}_{request.args.get('test_id')}.json","w") as f:
                json.dump(test,f)

    if test['score'] == 'NEHODNOCENO':
        score = 0
        for question in test['questions']:
            if question['type'] == 'full':
                continue
            if question['stud_answer'] == question['answer']:
                score += int(question['value'])
                question['earned'] = question['value']
            else:
                question['earned'] = 0
        test['score'] = score
        with open(f"test_students/test_{request.args.get('student_id')}_{request.args.get('test_id')}.json","w") as f:
            json.dump(test,f)
    
    return render_template('score_test.html', profile=session, test=test, answer = scoreform)

@app.route("/home/show_tests",methods=['GET','POST'])
def show_tests():
    #Get user ID
    user_id = session['id']
    #Querry DB
    db = dbSession()
    result = db.execute(f"SELECT `test_copy` FROM `registrations` WHERE `person_id` = '{user_id}' AND `approved` = '1' AND `person_type` = 'student' and `test_copy` is not null")
    db.close()
    my_test_files = [row[0] for row in result]
    tests = list()
    for test_file in my_test_files:
        with open(test_file,"r") as f:
            tests.append(json.load(f))

    cur_date = datetime.date.today()
    for test in tests:
        end_time_obj = datetime.datetime.strptime(test['config']['end'], '%m/%d/%Y')
        #only interested in done tests
        if (end_time_obj.date() > cur_date): 
            tests.remove(test)
            continue
    if request.method == "POST":
        if 'open' in request.form:
            for test in tests:
              if test['config']['id'] == int(request.form['open']):
                return render_template("show_tests.html", profile=session, tests=tests, opened = test['config']['id'])
  
    return render_template("show_tests.html", profile=session, tests=tests, opened = 'NO')


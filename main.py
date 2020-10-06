from flask import Flask, render_template, request, redirect, url_for, session
#from flask_mysqldb import MySQL
#import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'prdel'

# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', msg='')

    elif request.method == 'POST':
        #potrbujeme implementovat login
        return redirect(url_for('home'))

@app.route('/home/', methods=['GET', 'POST'])
def home():
    return render_template('home.html',msg='')
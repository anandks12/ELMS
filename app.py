from flask import Flask, url_for, request, session, g
from flask.templating import render_template
from werkzeug.utils import redirect
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'manager_db'):
        g.manager_db.close()

def get_current_user():
    manager = None
    if 'manager' in session:
        manager = session['manager']
        db = get_database()
        user_cur = db.execute('select * from users where name = ?', [manager])
        manager = user_cur.fetchone()
    return manager

@app.route('/',methods=["POST", "GET"])
def home():
    if request.method == 'POST':
        return render_template('elogin.html')
    else:    
        return render_template('index.html')
@app.route('/mhome')
def mhome():
    manager = get_current_user()
    return render_template('mhome.html', manager = manager)

   

@app.route('/login', methods = ["POST", "GET"])
def login():
    manager = get_current_user()
    error = None
    db = get_database()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        manager_cursor = db.execute('select * from users where name = ?', [name])
        manager = manager_cursor.fetchone()
        if manager:
            if check_password_hash(manager['password'], password):
                session['manager'] = manager['name']
                return redirect(url_for('dashboard'))
            else:
                error = "Username or Password did not match, Try again."
        else:
            error = 'Username or password did not match, Try again.'
    return render_template('login.html', loginerror = error, manager = manager)

@app.route('/register', methods=["POST", "GET"])
def register():
    manager = get_current_user()
    db = get_database()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        dbuser_cur = db.execute('select * from users where name = ?', [name])
        existing_username = dbuser_cur.fetchone()
        if existing_username:
            return render_template('register.html', registererror = 'Username already taken , try different username.')
        db.execute('insert into users ( name, password) values (?, ?)',[name, hashed_password])
        db.commit()
        return redirect(url_for('mhome'))
    return render_template('register.html', manager = manager)

@app.route('/dashboard')
def dashboard():
    manager = get_current_user()
    db = get_database()
    emp_cur = db.execute('select * from emp')
    allemp = emp_cur.fetchall()
    return render_template('dashboard.html', manager = manager, allemp = allemp)

@app.route('/addnewemployee', methods = ["POST", "GET"])
def addnewemployee():
    manager = get_current_user()
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        db = get_database()
        db.execute('insert into emp (name, email, phone ,address) values (?,?,?,?)', [name, email, phone, address])
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('addnewemployee.html', manager = manager)

@app.route('/singleemployee/<int:empid>')
def singleemployee(empid):
    manager = get_current_user()
    db = get_database()
    emp_cur = db.execute('select * from emp where empid = ?', [empid])
    single_emp = emp_cur.fetchone()
    return render_template('singleemployee.html', manager = manager, single_emp = single_emp)

@app.route('/fetchone/<int:empid>')
def fetchone(empid):
    manager = get_current_user()
    db = get_database()
    emp_cur = db.execute('select * from emp where empid = ?', [empid])
    single_emp = emp_cur.fetchone()
    return render_template('updateemployee.html', manager = manager, single_emp = single_emp)

@app.route('/updateemployee' , methods = ["POST", "GET"])
def updateemployee():
    manager = get_current_user()
    if request.method == 'POST':
        empid = request.form['empid']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        db = get_database()
        db.execute('update emp set name = ?, email =? , phone = ? , address = ? where empid = ?', [name, email, phone, address, empid])
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('updateemployee.html', manager = manager)

@app.route('/deleteemp/<int:empid>', methods = ["GET", "POST"])
def deleteemp(empid):
    manager = get_current_user()
    if request.method == 'GET':
        db = get_database()
        db.execute('delete from emp where empid = ?', [empid])
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', manager = manager)

@app.route('/logout')
def logout():
    session.pop('manager', None)
    render_template('mhome.html')
@app.route('/elogin', methods = ["POST", "GET"])    
def elogin():

   # emp = get_current_user()
    #error = None
    #db = get_database()
   # if request.method == 'POST':
    #    name = request.form['name']
     # password = request.form['password']
      #  emp_cursor = db.execute('select * from users where name = ?', [name])
       # emp = emp_cursor.fetchone()
        #if emp:
         #   if check_password_hash(emp['password'], password):
          #      session['manager'] = emp['name']
            #    return redirect(url_for('dashboard'))
           # else:
           #     error = "Username or Password did not match, Try again."
        #else:
         #   error = 'Username or password did not match, Try again.'
    if request.method=='POST':
        return render_template('elogin.html')#, loginerror = error, emp = emp)
    else:
        return render_template('elogin.html')    
 
if __name__ == '__main__':
    app.run(debug = True)
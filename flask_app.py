from flask import Flask, session, redirect, flash
from flask import url_for, escape, request, abort, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import pymysql.cursors
import pymysql, random

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'efsfsg'+ str(random.randint(1,999)) + \
 'swavdsvsd' + str(random.randint(1,101))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
connection = None

@app.route('/')
def index():
  return render_template('index.html', title = 'silverstone')


@app.route('/admin')
def hello_admin():
   return 'Hello Admin'

@app.route('/about')
def about():
  return render_template('about.html', name = 'user', title = 'about')

@app.route('/student')
def student():
   return render_template('students.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return render_template("result.html",result = result)


@app.route('/guest/<guest>')
def hello_guest(guest):
   return 'Hello %s as Guest' % guest


@app.route('/user/<name>')
def hello_user(name):
   if name =='admin':
      return redirect(url_for('hello_admin'))
   else:
      return redirect(url_for('hello_guest',guest = name))


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   global connection
   connection = None
   return redirect(url_for('index'))


@app.route('/success/<name>')
def success(name):
  try:
    if 'username' in session:
      username = session['username']
      print(username)
      return render_template('success.html', name = name, get_tenants_func = get_tenants)
  except Exception as e:
    print(e)
  return render_template('login.html')



@app.route('/login', methods=('GET', 'POST'))
def login():
    global connection

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        error = None

        connection = pymysql.connect(host='localhost', user='root',
          password='komezee1',db='silverstone',charset='utf8mb4',
          cursorclass=pymysql.cursors.DictCursor)

        if username is None:
            error = 'Incorrect username.'
        elif error is None:

            try:
                with connection.cursor() as cursor:
                    sql1 = "SELECT * FROM pass_kome_word WHERE username=%s"
                    cursor.execute(sql1, (username,))
                    result = cursor.fetchone()

                    if result is not None and check_password_hash(result['password'], password):
                        session.clear()
                        session['username'] = username
                        return redirect(url_for('success', name = username))
                    else:
                      error = 'Invalid Username and Password.'
            except Exception as e:
                error = 'SQL Error: ' + str(e)

        print(error)
    return render_template('login.html')




@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        error = None

        connection = pymysql.connect(host='localhost', user='root',
          password='komezee1',db='silverstone',charset='utf8mb4',
          cursorclass=pymysql.cursors.DictCursor)

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not firstname:
            error = 'First name is required.'
        elif not lastname:
            error = 'Last name is required.'
        elif error is None:
            try:
                with connection.cursor() as cursor:
                    sql1 = "SELECT idtenants FROM tenants WHERE first_name=%s"
                    cursor.execute(sql1, (firstname,))
                    result = cursor.fetchone()

                    if result is not None:
                        error = 'User {} is already registered.'.format(username)
            except Exception as e:
                error = 'SQL Error: ' + str(e)

            if error is None:
                try:
                    with connection.cursor() as cursor:
                        sql2 = "INSERT INTO tenants (first_name, last_name) VALUES (%s, %s)"
                        cursor.execute(sql2, (firstname, lastname))
                        connection.commit()

                        
                        sql3 = "SELECT idtenants FROM tenants WHERE first_name=%s"
                        cursor.execute(sql1, (firstname,))
                        result = cursor.fetchone()

                        print(result)

                        sql4 = "INSERT INTO pass_kome_word (tenants_idtenants, username, password) VALUES (%s, %s, %s)"
                        cursor.execute(sql4, (result.get('idtenants'), username, generate_password_hash(password)))
                        connection.commit()

                    return redirect(url_for('login'))
                except Exception as e:
                    print(str(e))
        flash(error)

    return render_template('register.html')


def get_tenants():
  with connection.cursor() as cursor: 
      sql1 = "SELECT * FROM tenants"
      cursor.execute(sql1) 
      results = cursor.fetchone() 
  return results


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run()
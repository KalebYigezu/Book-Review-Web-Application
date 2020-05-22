import os
import csv

from flask import Flask, session, render_template, request, redirect, url_for, g
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


class User:
    def __init__(self, id, user_name, email, password):
        self.id = id
        self.user_name = user_name
        self.email = email
        self.password = password


# Check for environment variable
if not os.getenv("MYDATAONHEROKU"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Set up database
engine = create_engine(os.getenv("MYDATAONHEROKU"))
db = scoped_session(sessionmaker(bind=engine))


@app.before_request
def before_request():
    g.user = None
    if 'id' in session:
        users = db.execute('select id, user_name, email, password from users where id = :id ',
                           {'id': session['id']}).fetchall()
        db_user = users[0]
        user = User(db_user.id, db_user.user_name, db_user.email, db_user.password)
        g.user = user



@app.route("/")
def index():
    return render_template("signinorup.html")


@app.route('/signout', methods=['POST', 'GET'])
def signout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/signin', methods=['POST', 'GET'])
def signin():

    if request.method == 'POST':
        session.pop('id', None)
        email = request.form.get('email')
        password = request.form.get('password')

        users = db.execute('select id, email, password from users where email = :email and password = :password',
                           {'email': email, 'password': password}).fetchall()

        if len(users) == 0:
            return redirect(url_for('badusernameorpw'))
        else:
            session['id'] = users[0].id
            return redirect(url_for('search'))
    else:
        return render_template("signin.html")


@app.route('/badusernameorpw')
def badusernameorpw():
    return render_template('badusernameorpw.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        psw = request.form.get("psw")
        psw_repeat = request.form.get("psw-repeat")

        db.execute(
            "insert into users (user_name, email, password, confirmed_password) values (:user_name, :email, :password, :confirmed_password)",
            {'user_name': username, 'email': email, 'password': psw, 'confirmed_password': psw_repeat})
        db.commit()
        return redirect(url_for('display'))
    else:
        return render_template("signup.html")


# will check if there is a user name and password matched with this in the database and give access
@app.route('/search', methods=['POST', 'GET'])
def search():
    if not g.user:
        return redirect(url_for('index'))
    return render_template('search.html')


@app.route('/display', methods=["POST", "GET"])
def display():
    return render_template('display.html')


@app.route('/selectedbooks', methods=['POST'])
def selected_books():
    if not g.user:
        return redirect(url_for('index'))
    search_results = '%' + request.form.get('search') +'%'
    books = db.execute('select isbn, author, title, yearr from books where isbn like :isbn or author like :author or title like :title',
                       {'yearr': search_results,'isbn': search_results, 'title': search_results, 'author': search_results}).fetchall()
    if len(books) == 0:
        return redirect(url_for('oops'))
    else:
        return render_template('selectedbooks.html', books=books)


@app.route('/bookdetail/<string:title>/<string:author>/<string:isbn>/<string:yearr>', methods=['POST', 'GET'])
def bookdetail(title, author, isbn, yearr):
    if not g.user:
        return redirect(url_for('index'))
    return render_template('bookdetail.html', title=title, author=author, isbn=isbn, yearr=yearr)


@app.route('/oops')
def oops():
    return render_template('oops.html')


if __name__ == "__main__":
    app.run(debug=True)
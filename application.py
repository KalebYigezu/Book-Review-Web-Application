import os
import csv

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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


@app.route("/")
def index():
    return render_template("signinorup.html")


@app.route('/signin')
def signin():
    return render_template("signin.html")


@app.route('/signup')
def signup():
    return render_template("signup.html")


# shows all the books found by the search
@app.route('/results')
def results():
    return render_template('results.html')


# will check if there is a user name and password matched with this in the database and give access
@app.route('/search', methods=['POST'])
def search():
    email = request.form.get('email')
    password = request.form.get('password')

    users = db.execute('select email, password from users where email = :email and password = :password',
                       {'email': email, 'password': password}).fetchall()

    if len(users) == 0:
        return render_template("badusernameorpw.html")
    else:
        return render_template('search.html')


@app.route('/display', methods=["POST"])
def display():
    username = request.form.get("username")
    email = request.form.get("email")
    psw = request.form.get("psw")
    psw_repeat = request.form.get("psw-repeat")

    db.execute(
        "insert into users (user_name, email, password, confirmed_password) values (:user_name, :email, :password, :confirmed_password)",
        {'user_name': username, 'email': email, 'password': psw, 'confirmed_password': psw_repeat})
    db.commit()
    return render_template('display.html')


if __name__ == "__main__":
    app.run(debug=True)

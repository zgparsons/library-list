import requests
import urllib.parse
import json
import re

from datetime import datetime
from flask import Flask, render_template, redirect, request, session, jsonify
from tempfile import mkdtemp
from flask_session import Session
from cs50 import SQL
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///libraryList.db")


@app.route('/', methods=["GET", "POST"])
def index():

    libraryinfo = {}
    if request.method == 'POST':
        if request.form.get('library') is None:
            return render_template('index.html')
        else:
            libraryinfo['name'] = request.form.get('library')

        # Strip ' library' from name
        bareName = libraryinfo['name'].title().replace(' Library', '')

        # Query db for Library
        rows = db.execute("SELECT * FROM libraries WHERE name = :name", name=bareName)
        if rows == []:
            rowsExists = False
            libraryinfo['name'] = (bareName + ' Library')
            # db.execute("INSERT INTO libraries (name, authority, address) VALUES (:name, :authority, :address)", name=bareName, authority=postcodeInfo['county'], address=libraryinfo['address'])
        else:
            rowsExists = True
            libraryinfo['name'] = rows[0]['name']
            libraryinfo['authority'] = rows[0]['authority']
            libraryinfo['address'] = rows[0]['address']

        if rows:
            return render_template('success.html', libraryinfo=libraryinfo)
        else:
           return render_template('add-library.html', libraryinfo=libraryinfo)

    else:
        rows = db.execute("SELECT * FROM libraries")
        return render_template('index.html', rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Todo - All commented out below is taken directly from CS50 finance.

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure user input for a username is made
        if not request.form.get("username"):
            return apology("must choose username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must choose password", 400)

        # Ensure password was confirmed
        if request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords don't match", 400)

        names = db.execute('SELECT DISTINCT username FROM users')
        user = {'username': request.form.get("username")}

        if names.count(user) == 1:
            return apology("must choose unique username", 400)
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :p)",
                       username=request.form.get('username'), p=generate_password_hash(request.form.get('password')))

            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))
            # Store ID in session
            session["user_id"] = rows[0]["id"]

        # Return user to homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    if request.method == "GET":

        username = request.args.get('username')
        users = db.execute("SELECT username FROM users WHERE username = :username", username=username)

        if len(username) > 0 and len(users) == 0:
            return jsonify(True)
        else:
            return jsonify(False)

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def lookupPostcode(postcode):
    try:
        url = requests.get(f'https://api.postcodes.io/postcodes/{postcode}')
        url.raise_for_status()
    except url.RequestException:
        return None

    try:
        info = url.json()
        return {
            "postcode": info["result"]["postcode"],
            "county": info["result"]["admin_county"],
            "region": info["result"]["region"]
        }
    except (KeyError, TypeError, ValueError):
        return None
import os
from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ud.db")

# Obtain weather info
url = 'https://api.aqi.in/api/v1/getMonitorsByCity'
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Authorization': 'eyJpdiI6ImJYXC9kaU5jakN0V0I1RlV0bU5CRklnPT0iLCJ2YWx1ZSI6Ik9jTWwzQ01XMFhBK2daZ3VBM3dwblE9PSIsIm1hYyI6ImIzZjE4ZGUxMmYyM2ZkMTA5NDY0YjM5YjE3YTMzNDdmYjJkNDU1OWIzMmMxNjg1YzQ1YmM4NWUwYWZiYTU0NTMifQ==',
    'Content-Type': 'application/json',
    'Cityname': 'Chennai'
}

# Make the GET request
response = requests.get(url, headers=headers)

# Store the response in a string
weather_data = response.text

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    userinfo = db.execute("SELECT * FROM users WHERE id = ?",session["user_id"])
    userinfo = userinfo[0]
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
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
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation don't match", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username doesn't exist
        if len(rows) == 1:
            return apology("username exists!", 400)
        # Adding to database
        db.execute("INSERT INTO users (username, hash) VALUES (?,?)",request.form.get("username"),generate_password_hash(request.form.get("password"), method='pbkdf2', salt_length=16))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
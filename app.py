import os
from cs50 import SQL
from flask import Flask, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from predictions import generate_predictions
from datetime import datetime, timedelta

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ud.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        city = request.form.get("search")
        # Pass the city name as a query parameter to /Prediction
        return redirect(url_for("get_weather", city=city))
    return render_template("index.html")

@app.route("/Prediction", methods=["GET", "POST"])
@login_required
def get_weather():
    # Retrieve city from the query parameters
    city = request.args.get("city", "Your City Name")  
    current_date = datetime.now().strftime("%Y-%m-%d")  

    # Generate predictions
    weather_data = generate_predictions()
    start_date = datetime.strptime("2022-10-21", "%Y-%m-%d")
    # Update each entry with incremented date
    for index, day in enumerate(weather_data):
        day["date"] = (start_date + timedelta(days=index)).strftime("%Y-%m-%d")
    
    return render_template("city.html", city_name=city, current_date=current_date, weather_data=weather_data)

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

@app.route("/reminder", methods=["GET", "POST"])
@login_required
def reminder():
    if request.method == "POST":
        email = request.form.get("Email")
        contact_number = request.form.get("cno")
        
        # Check if the user is already subscribed
        user_subscription = db.execute("SELECT is_subscribed FROM users WHERE id = ?", (session["user_id"],))
        
        if user_subscription and user_subscription[0]["is_subscribed"] == 1:
            # If the user is already subscribed, show message
            return render_template("reminder.html", message="Already on reminder list.")
        else:
            # If the user is not subscribed, update their subscription details
            db.execute("UPDATE users SET email = ?, contact_number = ?, is_subscribed = 1 WHERE id = ?",
                       (email, contact_number, session["user_id"]))
            return render_template("reminder.html", message="Successfully added to reminder list.")
    
    return render_template("reminder.html")


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
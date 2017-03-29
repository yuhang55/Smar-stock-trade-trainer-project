import sqlite3
import re
import time

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.hash import sha256_crypt
from tempfile import gettempdir

from func import *

app = Flask(__name__)

if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

app.jinja_env.filters["usd"] = usd

app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

file = "finance.db"
db = sqlite3.connect(file, check_same_thread=False)
c = db.cursor()


@app.route("/")
@login_required
def index():
    current_user = session["user_id"]
    current_cash = c.execute("SELECT cash FROM users WHERE id = :CURRENT_USER", [current_user]).fetchall()[0][0]
    available = c.execute("SELECT symbol, sum(quantity) FROM transactions WHERE user_id = :user_id GROUP BY symbol",
                          [session["user_id"]]).fetchall()
    stocks_value = 0
    for stock in available:
        stocks_value += (stock[1] * lookup(stock[0])["price"])
    c.execute("UPDATE users SET assets = :assets WHERE id = :user_id", [stocks_value, current_user])
    db.commit()
    return render_template("index.html", current_cash=current_cash, available=available, lookup=lookup, usd=usd, stocks_value=stocks_value)


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    current_user = session["user_id"]
    transactions = c.execute("SELECT * FROM transactions WHERE user_id = :user_id", [current_user]).fetchall()
    return render_template("history.html", transactions=transactions, lookup=lookup, usd=usd)
#test

@app.route("/leaderboard")
@login_required
def leaderboard():
    leaders = c.execute("SELECT username, cash, assets FROM users ORDER BY cash + assets DESC").fetchall()
    return render_template("leaderboard.html", leaders=leaders, usd=usd)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username")

        elif not request.form.get("password"):
            return apology("must provide password")

        c.execute("SELECT * FROM users WHERE username = :username", [request.form.get("username").lower()])
        all_rows = c.fetchall()

        if len(all_rows) != 1 or not sha256_crypt.verify(request.form.get("password"), all_rows[0][2]):
            return apology("invalid username and/or password")

        session["user_id"] = all_rows[0][0]

        return redirect(url_for("index"))

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    password_confirm = request.form.get("password-confirm")

    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        if not request.form.get("username"):
            return apology("Error","Forgot Username")
        elif not request.form.get("password"):
            return apology("Error", "Forgot Password")
        elif not request.form.get("password-confirm"):
            return apology("Error", "Forgot Confirmation")


        if password == password_confirm:
            hashed = sha256_crypt.encrypt(password)
            username = re.sub(r'\W+', '', username.lower())
            try:
                c.execute("INSERT INTO users(username, hash) VALUES(:username, :hash)", [username, hashed])
                db.commit()

                session["user_id"] = c.execute("SELECT * FROM users WHERE username = :username", [username]).fetchall()[0][0]

                return redirect(url_for("index"))

            except sqlite3.IntegrityError:
                return apology("Error", "Username taken")
        else:
            return apology("Passwords don't match")

if __name__ == "__main__":
    app.run(debug=True)

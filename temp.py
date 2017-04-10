import os
import sqlite3
import re
import time

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.hash import sha256_crypt
from tempfile import gettempdir

from helpers import *

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

def history():
    temp_dict={}
    transactions = c.execute("SELECT * FROM transactions").fetchall()
    for transaction in transactions:
        symbol=transaction[2]
        temp_dict[symbol]=symbol


    for symbol in temp_dict:
        time.sleep(5)
        price_dict=lookup(symbol)
        symbol=price_dict["symbol"]
        name=price_dict["name"]
        price=price_dict["price"]

        low=price_dict["low"]

        high=price_dict["high"]
        price=price_dict["price"]

        col2=price_dict["col2"]

        now = time.strftime("%s") 


        if not os.path.exists("static/"+symbol+".csv"):
           f=open("static/"+symbol+".csv",'w')
           print("Timestamp,close,high,low,open,volume",file=f, flush=True)
        else:
           f=open("static/"+symbol+".csv",'a+')
           print(now+","+str(price)+","+str(price)+","+str(high)+","+str(low)+","+str(col2),file=f, flush=True)
      

        #{'symbol': 'IWV', 'name': 'iShares Russell 3000 ETF', 'price': 139.59}


if __name__ == "__main__":
   history()

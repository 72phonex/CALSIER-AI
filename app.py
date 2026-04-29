# app.py
from flask import Flask, request, render_template, session, redirect
from calsifer import CalsiferCore
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET", "devsecret")
OWNER_KEY = os.environ.get("OWNER_KEY", "changeme")

users = {}

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        if user not in users:
            users[user] = generate_password_hash(pwd)
        if check_password_hash(users[user], pwd):
            session["user"] = user
            return redirect("/")
        return "Invalid login"
    return """
    <form method="post">
      <input name="username" placeholder="Username">
      <input name="password" placeholder="Password" type="password">
      <button>Login</button>
    </form>
    """

@app.route("/", methods=["GET","POST"])
def index():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        text = request.form["msg"]
        core = CalsiferCore(session["user"])
        reply = core.chat(text)
        return {"reply": reply}
    return render_template("index.html")

@app.route("/owner")
def owner():
    if request.args.get("key") != OWNER_KEY:
        return "Forbidden"
    conn = sqlite3.connect("calsifer.db")
    cur = conn.execute("SELECT * FROM patches")
    rows = cur.fetchall()
    return {"patches": rows}

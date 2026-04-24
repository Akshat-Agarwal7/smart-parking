
import os
from flask import Flask, render_template, jsonify, request, redirect, session
from datetime import datetime, timedelta
import sqlite3



app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

DB = "parking.db"


# 🧱 INIT DATABASE
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # bookings table
    c.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        slot INTEGER,
        end_time TEXT
    )
    """)

    # users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# 🔐 LOGIN REQUIRED HOME
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


# 🆕 SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template("signup.html")


# 🔑 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid credentials"

    return render_template("login.html")


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# 📊 GET SLOTS
@app.route("/slots")
def slots():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT slot, end_time FROM bookings")
    rows = c.fetchall()

    result = []

    for slot, end_time in rows:
        try:
            if end_time and datetime.fromisoformat(end_time) > datetime.now():
                result.append({
                    "slot": slot,
                    "end_time": end_time
                })
            else:
                c.execute("DELETE FROM bookings WHERE slot=?", (slot,))
        except:
            # 🔥 handle bad data safely
            c.execute("DELETE FROM bookings WHERE slot=?", (slot,))

    conn.commit()
    conn.close()

    return jsonify(result)

# 🚗 BOOK SLOT
@app.route("/book", methods=["POST"])
def book():
    data = request.json
    slot = data["slot"]
    duration = int(data["duration"])

    end_time = datetime.now() + timedelta(hours=duration)

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM bookings WHERE slot=?", (slot,))
    if c.fetchone():
        conn.close()
        return jsonify({"status": "error"})

    c.execute("INSERT INTO bookings VALUES (?, ?)", (slot, end_time.isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
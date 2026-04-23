from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)

DB = "parking.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS bookings (slot INTEGER)")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/slots")
def slots():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT slot FROM bookings")
    rows = c.fetchall()
    conn.close()

    return jsonify({
        "booked": [r[0] for r in rows]
    })

@app.route("/book", methods=["POST"])
def book():
    data = request.json
    slot = data["slot"]

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # 🔥 CHECK if already booked
    c.execute("SELECT * FROM bookings WHERE slot=?", (slot,))
    existing = c.fetchone()

    if existing:
        conn.close()
        return jsonify({"status": "error"})

    # ✅ insert if free
    c.execute("INSERT INTO bookings (slot) VALUES (?)", (slot,))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
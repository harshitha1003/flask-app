from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib
import os

app = Flask(__name__)

# -------------------------------
# Config for sessions
# -------------------------------
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key_123")
app.config["SESSION_COOKIE_SECURE"] = False  # True if HTTPS
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_PATH = "users.db"

# -------------------------------
# DB helper
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------------
# Create table if not exists
# -------------------------------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        hashed_pw = hash_password(password)

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed_pw)
        ).fetchone()
        conn.close()

        if user:
            session.clear()
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("signup"))

        hashed_pw = hash_password(password)

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_pw)
            )
            conn.commit()
            conn.close()

            # Auto login after signup
            session.clear()
            session["username"] = username
            flash("Signup successful! You are now logged in.", "success")
            return redirect(url_for("home"))

        except sqlite3.IntegrityError:
            flash("Username already exists.", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# -------------------------------
# Run the app
# -------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

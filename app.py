from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib
import os

# -----------------------
# Flask app setup
# -----------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key_123")
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_PATH = "users.db"

# -----------------------
# Helpers
# -----------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------
# Initialize DB and predefined usernames
# -----------------------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT,
            is_logged_in INTEGER DEFAULT 0
        )
    """)

    predefined_usernames = ["user1", "user2", "user3", "user4"]
    default_password = hash_password("12345")  # everyone gets this password

    for uname in predefined_usernames:
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (uname, default_password)
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

init_db()

# -----------------------
# Routes
# -----------------------
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
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user and user["password"] == hashed_pw:
            conn.execute("UPDATE users SET is_logged_in=1 WHERE username=?", (username,))
            conn.commit()
            conn.close()
            session.clear()
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "error")
            conn.close()

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    conn = get_db_connection()

    if request.method == "POST":
        roll_no = request.form["roll_no"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not roll_no or not username or not password:
            flash("All fields are required.", "error")
            conn.close()
            return redirect(url_for("signup"))

        hashed_pw = hash_password(password)
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user:
            flash("Username already exists.", "error")
            conn.close()
            return redirect(url_for("signup"))
        else:
            conn.execute(
                "INSERT INTO users (roll_no, username, password) VALUES (?, ?, ?)",
                (roll_no, username, hashed_pw)
            )
            conn.commit()
            flash("Signup successful! Please log in.", "success")
            conn.close()
            return redirect(url_for("login"))

    # GET request
    conn.close()
    return render_template("signup.html")

@app.route("/logout")
def logout():
    if "username" in session:
        conn = get_db_connection()
        conn.execute("UPDATE users SET is_logged_in=0 WHERE username=?", (session["username"],))
        conn.commit()
        conn.close()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/people")
def people():
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    conn = get_db_connection()
    users = conn.execute("SELECT username FROM users WHERE is_logged_in=1").fetchall()
    conn.close()
    
    return render_template("people.html", users=users)

# -----------------------
# Run app
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

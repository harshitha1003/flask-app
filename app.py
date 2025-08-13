from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flashing messages
DB_PATH = "users.db"

# -------------------------------
# Database helpers
# -------------------------------

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predefined_usernames (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Insert default usernames if table is empty
    cursor.execute("SELECT COUNT(*) FROM predefined_usernames")
    if cursor.fetchone()[0] == 0:
        for uname in ["unicorn", "phoenix", "dragon", "griffin", "pegasus"]:
            cursor.execute("INSERT OR IGNORE INTO predefined_usernames (username) VALUES (?)", (uname,))

    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# -------------------------------
# Routes
# -------------------------------

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = hash_password(password)

        try:
            cursor.execute(
                "INSERT INTO users (roll_no, username, password) VALUES (?, ?, ?)",
                (roll_no, username, hashed_pw)
            )
            conn.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already taken!", "error")

    # Fetch available usernames for dropdown
    cursor.execute("""
        SELECT username FROM predefined_usernames
        WHERE username NOT IN (SELECT username FROM users)
    """)
    available_users = [row['username'] for row in cursor.fetchall()]
    conn.close()

    return render_template("signup.html", available_users=available_users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = hash_password(password)

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed_pw)
        ).fetchone()
        conn.close()

        if user:
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

# -------------------------------
# Run server
# -------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

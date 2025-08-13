from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"  # needed for flashing messages

DB_PATH = "users.db"

# Helper: Get database connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Helper: hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Root route -> redirect to home
@app.route("/")
def index():
    return redirect(url_for("home"))

# Home page
@app.route("/home")
def home():
    return render_template("home.html")

# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    conn = get_db_connection()
    if request.method == "POST":
        roll_no = request.form["roll_no"]
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = hash_password(password)

        # Update existing user with empty password
        cursor = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=''",
            (username,)
        )
        user = cursor.fetchone()
        if user:
            conn.execute(
                "UPDATE users SET roll_no=?, password=? WHERE username=?",
                (roll_no, hashed_pw, username)
            )
            conn.commit()
            conn.close()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username is not available or already taken.", "error")

    # GET: show available usernames
    users = conn.execute("SELECT username FROM users WHERE password=''").fetchall()
    conn.close()
    return render_template("signup.html", available_users=users)

# Login page
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

if __name__ == "__main__":
    app.run(debug=True)

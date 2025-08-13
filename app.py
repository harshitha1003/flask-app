from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib
import os
from functools import wraps

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
# Login required decorator
# -----------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# -----------------------
# Initialize DB
# -----------------------
def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_logged_in INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            question TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            answer TEXT NOT NULL,
            karma INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(question_id) REFERENCES questions(id),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)

    # Predefined users with default password 12345
    predefined_usernames = ["user1", "user2", "user3", "user4"]
    default_password = hash_password("12345")
    for uname in predefined_usernames:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
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
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        hashed_pw = hash_password(password)

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and user["password"] == hashed_pw:
            session.clear()
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "error")

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
            return redirect(url_for("signup"))

        hashed_pw = hash_password(password)
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user:
            if not user["password"]:  # Allow signup if password is empty
                conn.execute(
                    "UPDATE users SET roll_no=?, password=? WHERE username=?",
                    (roll_no, hashed_pw, username)
                )
                conn.commit()
                flash("Signup successful! Please log in.", "success")
                conn.close()
                return redirect(url_for("login"))
            else:
                flash("Username already taken.", "error")
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

    # Fetch usernames with empty password to show in dropdown
    users = conn.execute("SELECT username FROM users WHERE password=''").fetchall()
    usernames = [row["username"] for row in users]
    conn.close()
    return render_template("signup.html", usernames=usernames)


    # Fetch usernames with empty password (if any)
    users = conn.execute("SELECT username FROM users WHERE password=''").fetchall()
    usernames = [row["username"] for row in users]
    conn.close()
    return render_template("signup.html", usernames=usernames)

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    conn = get_db_connection()
    if request.method == "POST":
        question_text = request.form.get("question", "").strip()
        if question_text:
            conn.execute(
                "INSERT INTO questions (username, question) VALUES (?, ?)",
                (session["username"], question_text)
            )
            conn.commit()
            flash("Question posted successfully!", "success")

    my_questions = conn.execute(
        "SELECT id, question, created_at FROM questions WHERE username=? ORDER BY created_at DESC",
        (session["username"],)
    ).fetchall()

    questions_with_answers = []
    for q in my_questions:
        answers = conn.execute(
            "SELECT id, username, answer, karma FROM answers WHERE question_id=? ORDER BY created_at ASC",
            (q["id"],)
        ).fetchall()
        q_dict = dict(q)
        q_dict["answers"] = [dict(a) for a in answers]
        questions_with_answers.append(q_dict)

    conn.close()
    return render_template("home.html", username=session["username"], questions=questions_with_answers)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# -----------------------
# Run app
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)

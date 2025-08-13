from flask import Flask, render_template, request, redirect, url_for, flash, session
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
            cursor.execute(
                "INSERT OR IGNORE INTO predefined_usernames (username) VALUES (?)",
                (uname,)
            )

    conn.commit()
    conn.close()

# Initialize DB on startup
if not os.path.exists(DB_PATH):
    init_db()
else:
    try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predefined_usernames")  # optional: clear old data
    for uname in ["unicorn", "phoenix", "dragon", "griffin", "pegasus"]:
        cursor.execute("INSERT OR IGNORE INTO predefined_usernames (username) VALUES (?)", (uname,))
    conn.commit()
    conn.close()

    except:
        init_db()


# -------------------------------
# Routes
# -------------------------------

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if "username" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])

@app.route("/signup", methods=["GET", "POST"])
def signup():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        roll_no = request.form["roll_no"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        hashed_pw = hash_password(password)

        print(f"[SIGNUP] roll_no={roll_no}, username={username}, hash={hashed_pw}")

        try:
            cursor.execute(
                "INSERT INTO users (roll_no, username, password) VALUES (?, ?, ?)",
                (roll_no, username, hashed_pw)
            )
            conn.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError as e:
            print(f"[SIGNUP ERROR] {e}")
            flash("Username already taken!", "error")

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
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        hashed_pw = hash_password(password)

        print(f"[LOGIN] entered_username={username}, entered_hash={hashed_pw}")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed_pw)
        ).fetchone()

        # Debug check: show stored hash if username exists
        if not user:
            stored_user = conn.execute(
                "SELECT * FROM users WHERE username=?",
                (username,)
            ).fetchone()
            if stored_user:
                print(f"[DEBUG] Stored hash for {username}: {stored_user['password']}")
            else:
                print(f"[DEBUG] No user found with username {username}")

        conn.close()

        if user:
            print(f"[LOGIN SUCCESS] {dict(user)}")
            session["username"] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("home"))
        else:
            print("[LOGIN FAILED] Invalid credentials")
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# -------------------------------
# Run server
# -------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

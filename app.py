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

@app.route("/")
def index():
    return redirect(url_for("login"))


# Home page
@app.route("/home")
def home():
    return render_template("home.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if request.method == 'POST':
        roll_no = request.form['roll_no']
        username = request.form['username']
        password = request.form['password']

        try:
            cursor.execute("INSERT INTO users (roll_no, username, password) VALUES (?, ?, ?)",
                           (roll_no, username, password))
            conn.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already taken!", "error")

    # GET request: show available usernames
    cursor.execute("""
        SELECT username FROM predefined_usernames
        WHERE username NOT IN (SELECT username FROM users)
    """)
    available_users = cursor.fetchall()
    conn.close()

    return render_template('signup.html', available_users=available_users)


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

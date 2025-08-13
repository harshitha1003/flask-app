from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # needed for flashing messages

DB_PATH = "users.db"

# Helper: Get predefined usernames
def get_usernames():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM predefined_usernames")
    usernames = [row[0] for row in cursor.fetchall()]
    conn.close()
    return usernames

# Home page
@app.route("/home")
def home():
    return render_template("home.html")

# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        roll_no = request.form["roll_no"]
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (roll_no, username, password) VALUES (?, ?, ?)",
                (roll_no, username, password),
            )
            conn.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already taken!", "error")
        finally:
            conn.close()

    usernames = get_usernames()
    return render_template("signup.html", usernames=usernames)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password),
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)


import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = get_db_connection()
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        username = request.form['username']
        password = request.form['password']

        # Update user entry if username already exists (from pre-defined list)
        conn.execute('UPDATE users SET roll_no=?, password=? WHERE username=?',
                     (roll_no, password, username))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    # GET request: show available usernames
    users = conn.execute('SELECT username FROM users WHERE password=""').fetchall()
    conn.close()
    return render_template('signup.html', available_users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?',
                            (username, password)).fetchone()
        conn.close()

        if user:
            return redirect(url_for('home'))
        else:
            return "Login failed"

    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)

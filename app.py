from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Fetch predefined usernames
    cursor.execute("SELECT username FROM predefined_usernames")
    usernames = [row[0] for row in cursor.fetchall()]

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "INSERT INTO users (roll_no, username, password) VALUES (?, ?, ?)",
            (roll_no, username, password),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("login"))

    conn.close()
    return render_template("signup.html", usernames=usernames)



    # Example usernames for selection
    usernames = ["user1", "user2", "user3"]
    return render_template("signup.html", usernames=usernames)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return "❌ Invalid username or password!"

    return render_template("login.html")

@app.route("/home")
def home():
    if "username" in session:
        return render_template("home.html", username=session["username"])
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="0.0.0.0", port=5000)

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

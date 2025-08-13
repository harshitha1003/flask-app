import sqlite3

DB_PATH = "users.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Users table: password can be NULL initially
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT,
    username TEXT NOT NULL UNIQUE,
    password TEXT,
    is_logged_in INTEGER DEFAULT 0
)
""")

# Insert predefined usernames with empty password
predefined_usernames = ["unicorn", "phoenix", "dragon", "griffin", "pegasus"]
for uname in predefined_usernames:
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, NULL)", (uname,))

conn.commit()
conn.close()
print("Database initialized successfully!")

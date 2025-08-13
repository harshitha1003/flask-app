import sqlite3

DB_PATH = "users.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -------------------------------
# Users table
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT,
    username TEXT NOT NULL UNIQUE,
    password TEXT,
    is_logged_in INTEGER DEFAULT 0
)
""")

# -------------------------------
# Questions table
# -------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    question TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(username) REFERENCES users(username)
)
""")

# -------------------------------
# Answers table
# -------------------------------
cursor.execute("""
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

# -------------------------------
# Predefined usernames with empty password and roll_no
# -------------------------------
predefined_usernames = ["user1", "user2", "user3", "user4"]

for uname in predefined_usernames:
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, roll_no, is_logged_in)
        VALUES (?, NULL, NULL, 0)
    """, (uname,))

conn.commit()
conn.close()
print("Database initialized successfully with users, questions, and answers tables!")

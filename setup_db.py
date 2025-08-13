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
    username TEXT UNIQUE NOT NULL,
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
# Predefined usernames with empty passwords
# -------------------------------
predefined_usernames = ["user1", "user2", "user3", "user4"]

for username in predefined_usernames:
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", 
            (username, "")
        )
        print(f"Added: {username}")
    except sqlite3.IntegrityError:
        print(f"Username {username} already exists, skipping.")

conn.commit()
conn.close()
print("Database setup complete with users, questions, and answers tables!")

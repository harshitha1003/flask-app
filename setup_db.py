import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create users table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT,
    is_logged_in INTEGER DEFAULT 0
)
""")

# Create questions table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    question TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Predefined usernames with empty passwords
predefined_usernames = ["user1", "user2", "user3", "user4"]

for username in predefined_usernames:
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, ""))
        print(f"Added: {username}")
    except sqlite3.IntegrityError:
        print(f"Username {username} already exists, skipping.")

conn.commit()
conn.close()
print("Setup complete!")

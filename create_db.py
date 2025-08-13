import sqlite3

# Connect to (or create) database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create table for predefined usernames
cursor.execute("""
CREATE TABLE IF NOT EXISTS predefined_usernames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE
)
""")

# Insert predefined usernames
predefined_usernames = ["unicorn", "phoenix", "dragon", "griffin", "pegasus"]

# Use INSERT OR IGNORE to avoid duplicates if script runs again
for uname in predefined_usernames:
    cursor.execute("INSERT OR IGNORE INTO predefined_usernames (username) VALUES (?)", (uname,))

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

# Commit changes and close
conn.commit()
conn.close()

print("Database created and tables initialized successfully!")

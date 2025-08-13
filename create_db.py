import sqlite3

# Connect to the database (it will create if not exists)
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create a table for users
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Optional: Pre-populate some usernames
predefined_usernames = ['unicorn', 'phoenix', 'dragon', 'griffin', 'pegasus']

for uname in predefined_usernames:
    try:
        c.execute('INSERT INTO users (roll_no, username, password) VALUES (?, ?, ?)',
                  ('', uname, ''))
    except sqlite3.IntegrityError:
        pass  # skip if username already exists

conn.commit()
conn.close()
print("Database created and usernames inserted.")

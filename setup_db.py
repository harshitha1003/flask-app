import sqlite3

# Connect to database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# List of predefined usernames to add
predefined_usernames = ["user1", "user2", "user3", "user4"]

# Insert usernames with empty password
for username in predefined_usernames:
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, ""))
        print(f"Added: {username}")
    except sqlite3.IntegrityError:
        print(f"Username {username} already exists, skipping.")

# Commit and close
conn.commit()
conn.close()
print("Done adding predefined usernames.")

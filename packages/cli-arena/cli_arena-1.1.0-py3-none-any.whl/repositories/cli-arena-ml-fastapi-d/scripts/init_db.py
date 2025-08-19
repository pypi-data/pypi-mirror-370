import sqlite3
from passlib.hash import bcrypt

# Connect to the database file (creates it if it doesn't exist)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Drop old tables if they exist (for clean re-runs)
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS prediction_logs")

# Create the 'users' table
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

# Create the 'prediction_logs' table
cursor.execute("""
CREATE TABLE prediction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    will_default BOOLEAN,
    timestamp TEXT
)
""")

# Add a sample user
cursor.execute(
    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
    ("user@example.com", bcrypt.hash("secret123"))
)

# Save and close
conn.commit()
conn.close()

print("users.db initialized with 'users' and 'prediction_logs' tables.")

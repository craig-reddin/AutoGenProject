import sqlite3

connection = sqlite3.connect('finance_dashboard.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Insert sample data
cur.execute("INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)",
            ('testuser', 'test@example.com', 'hashed_password'))

connection.commit()
connection.close()

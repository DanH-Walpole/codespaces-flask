import sqlite3

conn = sqlite3.connect("flaskapp.db")
cursor = conn.cursor()

# Check users table
print("Users in database:")
cursor.execute("SELECT id, username FROM users")
users = cursor.fetchall()
for user in users:
    print(f"User ID: {user[0]}, Username: {user[1]}")
    
# Check messages table
print("\nMessages in database:")
cursor.execute("SELECT id, content, user_id FROM messages")
messages = cursor.fetchall()
for message in messages:
    print(f"Message ID: {message[0]}, Content: {message[1]}, User ID: {message[2]}")
    
conn.close()

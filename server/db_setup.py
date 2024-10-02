# server/db_setup.py
import sqlite3
import hashlib
import os
from contextlib import closing

DATABASE = 'transfer_service.db'

def initialize_db():
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        # Create users table with salt
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                login_attempts INTEGER DEFAULT 0
            )
        ''')

        # Create uploads table for storing links, files, and images
        c.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY,
                uploader TEXT NOT NULL,
                file_type TEXT NOT NULL,  -- 'link', 'file', or 'image'
                content TEXT NOT NULL,    -- The actual link, filename, or file path
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Check if the 'salt' column exists in the users table and add it if missing
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        if 'salt' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN salt TEXT")
            update_existing_users_with_salts()  # Update existing users with salts

        conn.commit()

def generate_salt():
    return os.urandom(16).hex()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def update_existing_users_with_salts():
    """
    Updates existing users to include a unique salt and rehashes their passwords.
    """
    with closing(sqlite3.connect(DATABASE)) as conn, closing(conn.cursor()) as c:
        c.execute('SELECT id, password FROM users')
        users = c.fetchall()
        
        for user_id, password in users:
            salt = generate_salt()
            hashed_password = hash_password(password, salt)
            c.execute('UPDATE users SET password = ?, salt = ? WHERE id = ?', (hashed_password, salt, user_id))
        
        conn.commit()
        print("Updated existing users with salts.")

def add_user(username, password):
    # Generate a unique salt for each user
    salt = os.urandom(16)
    hashed_password = hashlib.sha256(salt + password.encode()).hexdigest()
    
    try:
        with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
            c.execute('INSERT INTO users (username, password, salt) VALUES (?, ?, ?)', (username, hashed_password, salt))
            conn.commit()
            print(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")

def delete_user(username):
    """
    Deletes a user from the database based on the provided username.
    """
    try:
        with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
            c.execute('DELETE FROM users WHERE username = ?', (username,))
            conn.commit()
            print(f"User '{username}' deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting user '{username}': {e}")

def get_user(username):
    with closing(sqlite3.connect(DATABASE)) as conn, closing(conn.cursor()) as c:
        # Select only password, salt, and login_attempts
        c.execute('SELECT password, salt, login_attempts FROM users WHERE username = ?', (username,))
        return c.fetchone()

def reset_login_attempts(username):
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        c.execute('UPDATE users SET login_attempts = 0 WHERE username = ?', (username,))
        conn.commit()

def increment_login_attempts(username):
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        if username:
            c.execute('UPDATE users SET login_attempts = login_attempts + 1 WHERE username = ?', (username,))
            c.execute('SELECT login_attempts FROM users WHERE username = ?', (username,))
            login_attempts = c.fetchone()[0]
            conn.commit()
            return login_attempts
        else:
            return None

def add_upload(uploader, file_type, content):
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        c.execute('INSERT INTO uploads (uploader, file_type, content) VALUES (?, ?, ?)', (uploader, file_type, content))
        conn.commit()

def get_uploads():
    with closing(sqlite3.connect(DATABASE)) as conn, closing(conn.cursor()) as c:
        c.execute('SELECT id, uploader, file_type, content FROM uploads')
        return c.fetchall()

def delete_upload(upload_id):
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        c.execute('DELETE FROM uploads WHERE id = ?', (upload_id,))
        conn.commit()

def update_upload_filename(upload_id, new_name):
    with closing(sqlite3.connect(DATABASE)) as conn, closing(conn.cursor()) as c:
        c.execute('UPDATE uploads SET content = ? WHERE id = ?', (new_name, upload_id))
        conn.commit()

if __name__ == '__main__':
    initialize_db()

    # Example of initializing users (only run manually)
    # add_user('iphone_user', 'your_secure_password')
    # add_user('laptop_user', 'your_secure_password')
    # Example of deleting user
    # delete_user('iphone_user')
    # delete_user('laptop_user')

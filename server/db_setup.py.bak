# server/db_setup.py
import sqlite3
import hashlib
from contextlib import closing

DATABASE = 'transfer_service.db'

def initialize_db():
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
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

        conn.commit()

def add_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            print(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"User '{username}' already exists.")

def get_user(username):
    with closing(sqlite3.connect(DATABASE)) as conn, closing(conn.cursor()) as c:
        c.execute('SELECT username, password, login_attempts FROM users WHERE username = ?', (username,))
        return c.fetchone()

def reset_login_attempts(username):
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        c.execute('UPDATE users SET login_attempts = 0 WHERE username = ?', (username,))
        conn.commit()

def increment_login_attempts(username):
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        c.execute('UPDATE users SET login_attempts = login_attempts + 1 WHERE username = ?', (username,))
        conn.commit()

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

if __name__ == '__main__':
    initialize_db()
    # Example of initializing users (only run manually)
#    add_user('iphone_user', 'your_secure_password')
#    add_user('laptop_user', 'your_secure_password')

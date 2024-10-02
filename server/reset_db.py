import os
import sqlite3
from contextlib import closing

DATABASE = 'transfer_service.db'

def reset_database():
    # Remove the existing database file
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print(f"Removed existing database '{DATABASE}'.")

    # Recreate the database structure
    with closing(sqlite3.connect(DATABASE)) as conn, conn, closing(conn.cursor()) as c:
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,  -- Added salt column
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
        print("Database initialized successfully.")

if __name__ == '__main__':
    reset_database()

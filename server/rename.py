# rename.py
import os
import sqlite3

UPLOAD_DIRECTORY = "../assets"
DATABASE = 'transfer_service.db'  # Define the DATABASE path

def rename_file(upload_id, new_name):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Retrieve the upload record based on the ID
    c.execute('SELECT * FROM uploads WHERE id = ?', (upload_id,))
    upload = c.fetchone()
    
    if not upload:
        conn.close()
        return False, "File not found in database"
    
    old_filename = upload[3]
    old_path = os.path.join(UPLOAD_DIRECTORY, old_filename)
    new_path = os.path.join(UPLOAD_DIRECTORY, new_name)

    if os.path.exists(new_path):
        conn.close()
        return False, "A file with the new name already exists"

    # Rename the file in the filesystem
    try:
        os.rename(old_path, new_path)
    except OSError as e:
        conn.close()
        return False, f"Error renaming file: {e}"

    # Update the filename in the database
    c.execute('UPDATE uploads SET content = ? WHERE id = ?', (new_name, upload_id))
    conn.commit()
    conn.close()
    
    return True, "File renamed successfully"

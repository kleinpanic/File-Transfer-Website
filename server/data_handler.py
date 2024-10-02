import os
import sqlite3  # Ensure sqlite3 is imported
from db_setup import add_upload, get_uploads, DATABASE

UPLOAD_DIRECTORY = "../assets"  # Directory to store uploaded files

def save_link(uploader, link):
    add_upload(uploader, 'link', link)

def save_file(uploader, file):
    # Ensure upload directory exists
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    file.save(file_path)
    add_upload(uploader, 'file', file.filename)

def retrieve_uploads():
    return get_uploads()

def handle_download(upload_id, uploader=None, delete_only=False):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Fetch the upload entry by ID only (remove the uploader check)
    c.execute('SELECT * FROM uploads WHERE id = ?', (upload_id,))
    upload = c.fetchone()

    if not upload:
        print(f"Error: No entry found in the database for ID {upload_id}")
        conn.close()
        return None
    
    if delete_only:
        # Delete the entry from the database
        c.execute('DELETE FROM uploads WHERE id = ?', (upload_id,))
        conn.commit()
        
        # Additionally, remove the file from the filesystem if it is a file upload
        if upload[2] == 'file':
            file_path = get_file_path(upload[3])
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Successfully removed file from filesystem: {file_path}")
            else:
                print(f"File not found in filesystem, could not delete: {file_path}")
        
        conn.close()
        return None

    conn.close()
    return upload

def get_file_path(filename):
    return os.path.abspath(os.path.join(UPLOAD_DIRECTORY, filename))

# preview.py
import os
from flask import send_file, jsonify
import sqlite3
import mimetypes

UPLOAD_DIRECTORY = "../assets"

def generate_preview(upload_id):
    conn = sqlite3.connect('transfer_service.db')
    c = conn.cursor()
    
    c.execute('SELECT file_type, content FROM uploads WHERE id = ?', (upload_id,))
    upload = c.fetchone()
    
    if not upload:
        conn.close()
        return jsonify({"error": "File not found"}), 404
    
    file_type, filename = upload
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Detect the MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    
    # Handle different file types for preview
    if file_type == "link":
        return jsonify({"link": filename}), 200
    
    # Send the file with the correct MIME type
    if file_type == "file" and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return send_file(file_path, mimetype='image/jpeg', download_name=os.path.basename(file_path))    

    return jsonify({"error": "Preview not supported for this file type"}), 400

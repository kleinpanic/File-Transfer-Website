# server/app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
from flask_talisman import Talisman
import os

app = Flask(__name__, template_folder='../templates')
Talisman(app)

RECEIVED_FILES_DIR = "../assets"
if not os.path.exists(RECEIVED_FILES_DIR):
    os.makedirs(RECEIVED_FILES_DIR)

# Data storage for links and images
uploaded_links = []
uploaded_images = []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload/link', methods=['POST'])
def upload_link():
    data = request.form
    if 'link' not in data or 'uploader' not in data:
        return jsonify({"error": "Link and uploader's name are required"}), 400
    
    link_info = {'link': data['link'], 'uploader': data['uploader']}
    uploaded_links.append(link_info)
    
    with open(os.path.join(RECEIVED_FILES_DIR, "links.txt"), "a") as f:
        f.write(f"{data['uploader']}: {data['link']}\n")

    return redirect(url_for('index'))

@app.route('/upload/image', methods=['POST'])
def upload_image():
    if 'file' not in request.files or 'uploader' not in request.form:
        return jsonify({"error": "File and uploader's name are required"}), 400

    file = request.files['file']
    uploader = request.form['uploader']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    save_path = os.path.join(RECEIVED_FILES_DIR, file.filename)
    file.save(save_path)
    
    uploaded_images.append({'filename': file.filename, 'uploader': uploader})
    
    return redirect(url_for('index'))

@app.route('/uploads')
def view_uploads():
    return render_template("uploads.html", links=uploaded_links, images=uploaded_images)

@app.route('/assets/<filename>')
def get_image(filename):
    return send_from_directory(RECEIVED_FILES_DIR, filename)

@app.route('/rename/<filename>', methods=['POST'])
def rename_file(filename):
    new_name = request.form.get('new_name')
    if new_name and os.path.exists(os.path.join(RECEIVED_FILES_DIR, filename)):
        os.rename(os.path.join(RECEIVED_FILES_DIR, filename), os.path.join(RECEIVED_FILES_DIR, new_name))
        
        # Update internal records
        for image in uploaded_images:
            if image['filename'] == filename:
                image['filename'] = new_name
                break
                
        return redirect(url_for('view_uploads'))
    return jsonify({"error": "Invalid file name"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')


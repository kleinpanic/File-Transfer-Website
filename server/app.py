# server/app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_talisman import Talisman
import os
from security import validate_user, identify_uploader

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'super_secret_key'  # Change this to a more secure key for production
Talisman(app)

RECEIVED_FILES_DIR = "../assets"
if not os.path.exists(RECEIVED_FILES_DIR):
    os.makedirs(RECEIVED_FILES_DIR)

# Data storage for links and images
uploaded_links = []
uploaded_images = []

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid credentials. Please try again.", 403
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload/link', methods=['POST'])
def upload_link():
    if 'username' not in session:
        return redirect(url_for('login'))

    data = request.form
    if 'link' not in data:
        return jsonify({"error": "No link provided"}), 400
    
    uploader = identify_uploader()
    link_info = {'link': data['link'], 'uploader': uploader}
    uploaded_links.append(link_info)
    
    with open(os.path.join(RECEIVED_FILES_DIR, "links.txt"), "a") as f:
        f.write(f"{uploader}: {data['link']}\n")

    return redirect(url_for('index'))

@app.route('/upload/image', methods=['POST'])
def upload_image():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    uploader = identify_uploader()
    save_path = os.path.join(RECEIVED_FILES_DIR, file.filename)
    file.save(save_path)
    
    uploaded_images.append({'filename': file.filename, 'uploader': uploader})
    
    return redirect(url_for('index'))

@app.route('/uploads')
def view_uploads():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("uploads.html", links=uploaded_links, images=uploaded_images)

@app.route('/assets/<filename>')
def get_image(filename):
    return send_from_directory(RECEIVED_FILES_DIR, filename)

@app.route('/rename/<filename>', methods=['POST'])
def rename_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))

    new_name = request.form.get('new_name')
    if new_name and os.path.exists(os.path.join(RECEIVED_FILES_DIR, filename)):
        os.rename(os.path.join(RECEIVED_FILES_DIR, filename), os.path.join(RECEIVED_FILES_DIR, new_name))
        
        for image in uploaded_images:
            if image['filename'] == filename:
                image['filename'] = new_name
                break
                
        return redirect(url_for('view_uploads'))
    return jsonify({"error": "Invalid file name"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')

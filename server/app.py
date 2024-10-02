from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory, jsonify, send_file
from flask_talisman import Talisman
from functools import wraps
import os
from security import validate_user
from data_handler import save_link, save_file, retrieve_uploads, handle_download, get_file_path
from datetime import datetime
from zipfile import ZipFile
from preview import generate_preview  # Import the preview module
from rename import rename_file  # Import the rename module

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.urandom(24)
talisman = Talisman(app, content_security_policy={
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"]
})

UPLOAD_DIRECTORY = "../assets"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

DOWNLOADS_DIRECTORY = os.path.expanduser("~/Downloads")
if not os.path.exists(DOWNLOADS_DIRECTORY):
    os.makedirs(DOWNLOADS_DIRECTORY)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            print("User is not logged in, redirecting to login page")
            return redirect(url_for('login', next=request.url))
        print("User is logged in, proceeding to requested page")
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def ensure_login():
    if 'username' not in session and request.endpoint not in ('login', 'static'):
        return redirect(url_for('login'))
    elif request.endpoint == 'login' and 'username' in session:
        session.clear()

@app.route('/')
@login_required
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        valid, message = validate_user(username, password)
        
        if valid:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error=message)

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/upload/link', methods=['POST'])
@login_required
def upload_link():
    link = request.form['link']
    uploader = session['username']
    save_link(uploader, link)
    return redirect(url_for('index'))

@app.route('/upload/files', methods=['POST'])
@login_required
def upload_files():
    if 'files' not in request.files:
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    uploader = session['username']
    
    for file in files:
        save_file(uploader, file)
    
    return redirect(url_for('index'))

@app.route('/uploads')
@login_required
def view_uploads():
    uploads = retrieve_uploads()
    
    links = [upload for upload in uploads if upload[2] == 'link']
    videos = [upload for upload in uploads if upload[2] == 'file' and upload[3].lower().endswith(('.mp4', '.mkv', '.avi'))]
    photos = [upload for upload in uploads if upload[2] == 'file' and upload[3].lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    misc = [upload for upload in uploads if upload[2] == 'file' and upload not in videos + photos]

    return render_template(
        "uploads.html", 
        links=links, 
        videos=videos, 
        photos=photos, 
        misc=misc, 
        username=session['username']
    )

@app.route('/download_link/<int:link_id>', methods=['GET'])
@login_required
def download_link(link_id):
    upload = handle_download(link_id)

    if upload and upload[2] == 'link':
        link_content = upload[3]
        x = 1
        while os.path.exists(os.path.join(DOWNLOADS_DIRECTORY, f"link_{x}.txt")):
            x += 1
        filename = f"link_{x}.txt"
        filepath = os.path.join(DOWNLOADS_DIRECTORY, filename)
        with open(filepath, 'w') as f:
            f.write(link_content)

        response = send_from_directory(DOWNLOADS_DIRECTORY, filename, as_attachment=True)

        handle_download(link_id, delete_only=True)
        return response
    return "Link Not found", 404

@app.route('/download_all_links', methods=['GET'])
@login_required
def download_all_links():
    links = [upload for upload in retrieve_uploads() if upload[2] == 'link']

    if len(links) > 1:
        current_date = datetime.now().strftime("%m-%d-%Y")
        filename = f"links_{current_date}.txt"
        
        links_file_path = os.path.join(DOWNLOADS_DIRECTORY, filename)
        with open(links_file_path, 'w') as f:
            for link in links:
                f.write(link[3] + "\n")

        response = send_from_directory(DOWNLOADS_DIRECTORY, filename, as_attachment=True)
        for link in links:
            handle_download(link[0], delete_only=True)
        return response
    else:
        return redirect(url_for('view_uploads'))

@app.route('/download/<int:upload_id>', methods=['GET'])
@login_required
def download(upload_id):
    upload = handle_download(upload_id)

    if upload and upload[2] == 'file':
        file_path = get_file_path(upload[3])
        if not os.path.isfile(file_path):
            return redirect(url_for('view_uploads'), code=404)

        response = send_from_directory(
            directory=os.path.dirname(file_path),
            path=os.path.basename(file_path),
            as_attachment=True,
            #download_name=os.path.basename(file_path)  # Ensures the download retains the current name
            download_name=upload[3]
        )

        handle_download(upload_id, delete_only=True)
        return response 
    return "The requested file does not exist or you do not have permission to access it.", 404

@app.route('/delete_link/<int:link_id>', methods=['GET'])
@login_required
def delete_link(link_id):
    handle_download(link_id, delete_only=True)
    return redirect(url_for('view_uploads'))

@app.route('/delete_file/<int:file_id>', methods=['GET'])
@login_required
def delete_file(file_id):
    handle_download(file_id, delete_only=True)
    return redirect(url_for('view_uploads'))

# Add routes for downloading all photos
@app.route('/download_all_photos', methods=['GET'])
@login_required
def download_all_photos():
    photos = [upload for upload in retrieve_uploads() if upload[2] == 'file' and upload[3].lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

    if photos:
        zip_filename = f"photos_{datetime.now().strftime('%m-%d-%Y')}.zip"
        zip_filepath = os.path.join(DOWNLOADS_DIRECTORY, zip_filename)

        # Create a zip file containing all photos
        with ZipFile(zip_filepath, 'w') as zipf:
            for photo in photos:
                file_path = get_file_path(photo[3])
                zipf.write(file_path, os.path.basename(file_path))
                handle_download(photo[0], delete_only=True)  # Delete each photo entry

        return send_from_directory(DOWNLOADS_DIRECTORY, zip_filename, as_attachment=True)
    else:
        return redirect(url_for('view_uploads'))

# Add similar routes for videos and misc
@app.route('/download_all_videos', methods=['GET'])
@login_required
def download_all_videos():
    videos = [upload for upload in retrieve_uploads() if upload[2] == 'file' and upload[3].lower().endswith(('.mp4', '.mkv', '.avi'))]

    if videos:
        zip_filename = f"videos_{datetime.now().strftime('%m-%d-%Y')}.zip"
        zip_filepath = os.path.join(DOWNLOADS_DIRECTORY, zip_filename)

        with ZipFile(zip_filepath, 'w') as zipf:
            for video in videos:
                file_path = get_file_path(video[3])
                zipf.write(file_path, os.path.basename(file_path))
                handle_download(video[0], delete_only=True)  # Delete each video entry

        return send_from_directory(DOWNLOADS_DIRECTORY, zip_filename, as_attachment=True)
    else:
        return redirect(url_for('view_uploads'))

@app.route('/download_all_misc', methods=['GET'])
@login_required
def download_all_misc():
    misc_files = [upload for upload in retrieve_uploads() if upload[2] == 'file' and upload not in videos + photos]

    if misc_files:
        zip_filename = f"misc_{datetime.now().strftime('%m-%d-%Y')}.zip"
        zip_filepath = os.path.join(DOWNLOADS_DIRECTORY, zip_filename)

        with ZipFile(zip_filepath, 'w') as zipf:
            for item in misc_files:
                file_path = get_file_path(item[3])
                zipf.write(file_path, os.path.basename(file_path))
                handle_download(item[0], delete_only=True)  # Delete each misc entry

        return send_from_directory(DOWNLOADS_DIRECTORY, zip_filename, as_attachment=True)
    else:
        return redirect(url_for('view_uploads'))

# Route to handle file renaming
@app.route('/rename/<int:upload_id>', methods=['POST'])
@login_required
def rename(upload_id):
    data = request.get_json()  # Expecting JSON data from the frontend
    new_name = data.get('new_name', '').strip()
    
    if not new_name:
        return jsonify({"error": "New name not provided"}), 400
    
    success, message = rename_file(upload_id, new_name)
    
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": message}), 400

# Route to handle file previews
@app.route('/preview/<int:upload_id>', methods=['GET'])
@login_required
def preview(upload_id):
    return generate_preview(upload_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')

# server/security.py
from flask import request, session
import hashlib
from db_setup import get_user, increment_login_attempts, reset_login_attempts

MAX_ATTEMPTS = 3

def validate_user(username, password):
    user_data = get_user(username)
    if not user_data:
        return False, "User does not exist."

    stored_username, stored_password, login_attempts = user_data

    if login_attempts >= MAX_ATTEMPTS:
        return False, "Maximum login attempts exceeded. Please contact the administrator."

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    if hashed_password == stored_password:
        reset_login_attempts(username)
        return True, "Login successful."
    else:
        increment_login_attempts(username)
        return False, f"Invalid credentials. {MAX_ATTEMPTS - login_attempts - 1} attempt(s) remaining."

def identify_uploader():
    device_info = get_device_info()
    if "iPhone" in device_info['user_agent']:
        return f"Uploaded by iPhone (IP: {device_info['ip']})"
    else:
        return f"Uploaded by {device_info['isa']} {device_info['os']} (IP: {device_info['ip']})"

def get_device_info():
    user_agent = request.headers.get('User-Agent', 'Unknown')
    return {
        "ip": request.remote_addr,
        "user_agent": user_agent,
    }


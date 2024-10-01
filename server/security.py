# server/security.py
from flask import request
import platform
import hashlib

# Mock user database (username: password) - replace with a real database
USER_DATABASE = {
    "iphone_user": hashlib.sha256("iphone_password".encode()).hexdigest(),
    "laptop_user": hashlib.sha256("laptop_password".encode()).hexdigest(),
}

# Function to validate user credentials
def validate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return USER_DATABASE.get(username) == hashed_password

# Function to extract device information
def get_device_info():
    user_agent = request.headers.get('User-Agent', 'Unknown')
    return {
        "ip": request.remote_addr,
        "user_agent": user_agent,
        "isa": platform.machine(),  # Get system architecture
        "os": platform.system(),    # Get OS
    }

# Function to identify the uploader based on device info
def identify_uploader():
    device_info = get_device_info()
    if "iPhone" in device_info['user_agent']:
        return f"Uploaded by iPhone (IP: {device_info['ip']})"
    else:
        return f"Uploaded by {device_info['isa']} {device_info['os']} (IP: {device_info['ip']})"

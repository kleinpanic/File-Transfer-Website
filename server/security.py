import os  # Import for generating random salts
import hashlib
from flask import request
from db_setup import get_user, increment_login_attempts, reset_login_attempts

MAX_ATTEMPTS = 3

def generate_salt():
    """
    Generates a 16-byte random salt.
    """
    return os.urandom(16)

def hash_password(password, salt):
    # Convert the salt to bytes if it's a string
    if isinstance(salt, str):
        salt = salt.encode()
    return hashlib.sha256(salt + password.encode()).hexdigest()

def validate_user(username, password):
    """
    Validates the user's credentials against stored data.
    """
    user_data = get_user(username)
    if not user_data:
        print(f"User '{username}' does not exist.")
        return False, "User does not exist."

    stored_password, salt, login_attempts = user_data

    # Check if the maximum login attempts have been reached
    if login_attempts >= MAX_ATTEMPTS:
        print(f"User '{username}' has exceeded max login attempts.")
        return False, "Maximum login attempts exceeded. Please contact the administrator."

    # Hash the provided password with the salt
    hashed_password = hash_password(password, salt)
    print(f"Provided hash: {hashed_password}, Stored hash: {stored_password}")

    if hashed_password == stored_password:
        reset_login_attempts(username)
        print(f"User '{username}' logged in successfully.")
        return True, "Login successful."
    else:
        increment_login_attempts(username)
        remaining_attempts = MAX_ATTEMPTS - login_attempts - 1
        print(f"Invalid credentials for '{username}'. {remaining_attempts} attempt(s) remaining.")
        return False, f"Invalid credentials. {remaining_attempts} attempt(s) remaining."

def identify_uploader():
    """
    Identifies the uploader's device information from the request headers.
    """
    device_info = get_device_info()
    user_agent = device_info['user_agent']

    if "iPhone" in user_agent:
        device_type = "iPhone"
    elif "Android" in user_agent:
        device_type = "Android"
    elif "Windows" in user_agent:
        device_type = "Windows PC"
    elif "Mac" in user_agent:
        device_type = "Mac"
    elif "Linux" in user_agent:
        device_type = "Linux Machine"
    else:
        device_type = "Unknown Device"

    return f"Uploaded by {device_type} (IP: {device_info['ip']})"

def get_device_info():
    """
    Extracts device information from the request.
    """
    return {
        "ip": request.remote_addr or "Unknown IP",
        "user_agent": request.headers.get('User-Agent', 'Unknown'),
    }

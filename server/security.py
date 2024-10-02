import os
import hashlib
from flask import request
from db_setup import get_user, increment_login_attempts, reset_login_attempts

MAX_ATTEMPTS = 3
LOCKOUT_FILE = "locked_ips.txt"
FAILED_ATTEMPTS = {}

# Ensure the locked_ips.txt file exists
if not os.path.exists(LOCKOUT_FILE):
    with open(LOCKOUT_FILE, 'w') as f:
        pass

def generate_salt():
    """
    Generates a 16-byte random salt.
    """
    return os.urandom(16)

def hash_password(password, salt):
    """
    Hashes the password with the provided salt using SHA-256.
    """
    # Convert the salt to bytes if it's a string
    if isinstance(salt, str):
        salt = salt.encode()
    return hashlib.sha256(salt + password.encode()).hexdigest()

def is_ip_locked(ip):
    """
    Checks if the IP address is in the lockout list.
    """
    if os.path.exists(LOCKOUT_FILE):
        with open(LOCKOUT_FILE, 'r') as f:
            locked_ips = f.read().splitlines()
            return ip in locked_ips
    return False

def lock_ip(ip):
    """
    Adds an IP address to the lockout list.
    """
    with open(LOCKOUT_FILE, 'a') as f:
        f.write(ip + "\n")

def validate_user(username, password):
    ip_address = request.remote_addr

    # Check if the IP is locked
    if is_ip_locked(ip_address):
        return False, "You have been locked out."

    # Check or increment failed attempts for this IP address
    if ip_address not in FAILED_ATTEMPTS:
        FAILED_ATTEMPTS[ip_address] = 0

    user_data = get_user(username)
    if not user_data:
        FAILED_ATTEMPTS[ip_address] += 1

        if FAILED_ATTEMPTS[ip_address] >= MAX_ATTEMPTS:
            lock_ip(ip_address)
            return False, "Maximum login attempts exceeded. You have been locked out."
        
        remaining_attempts = MAX_ATTEMPTS - FAILED_ATTEMPTS[ip_address]
        return False, f"User does not exist. {remaining_attempts} attempt(s) remaining."

    stored_password, salt, login_attempts = user_data

    hashed_password = hash_password(password, salt)
    if hashed_password == stored_password:
        reset_login_attempts(username)
        # Clear failed attempts for this IP on a successful login
        FAILED_ATTEMPTS.pop(ip_address, None)
        return True, "Login successful."
    else:
        FAILED_ATTEMPTS[ip_address] += 1
        if FAILED_ATTEMPTS[ip_address] >= MAX_ATTEMPTS:
            lock_ip(ip_address)
            return False, "Maximum login attempts exceeded. You have been locked out."
        
        remaining_attempts = MAX_ATTEMPTS - FAILED_ATTEMPTS[ip_address]
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

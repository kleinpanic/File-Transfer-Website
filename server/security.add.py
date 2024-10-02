def validate_user(username, password):
    ip_address = request.remote_addr

    # Check if the IP is locked
    if is_ip_locked(ip_address):
        return False, "You have been locked out."

    user_data = get_user(username)
    if not user_data:
        increment_login_attempts(None)  # Increment failed attempts for any non-existent username attempt
        
        # Check if IP should be locked
        attempts = increment_login_attempts(None)
        if attempts >= MAX_ATTEMPTS:
            lock_ip(ip_address)
            return False, "Maximum login attempts exceeded. You have been locked out."
        
        remaining_attempts = MAX_ATTEMPTS - attempts
        return False, f"User does not exist. {remaining_attempts} attempt(s) remaining."

    stored_password, salt, login_attempts = user_data

    # Check if the maximum login attempts have been reached
    if login_attempts >= MAX_ATTEMPTS:
        lock_ip(ip_address)
        return False, "Maximum login attempts exceeded. You have been locked out."

    hashed_password = hash_password(password, salt)
    if hashed_password == stored_password:
        reset_login_attempts(username)
        return True, "Login successful."
    else:
        increment_login_attempts(username)
        if login_attempts + 1 >= MAX_ATTEMPTS:
            lock_ip(ip_address)
            return False, "Maximum login attempts exceeded. You have been locked out."
        
        remaining_attempts = MAX_ATTEMPTS - login_attempts - 1
        return False, f"Invalid credentials. {remaining_attempts} attempt(s) remaining."

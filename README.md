# iPhone-Linux Transfer Service

A web-based application for transferring files and links between iPhone and Linux devices with a secure and user-friendly interface.

## Features
- **Upload and manage links and files:** Upload HTML links, images, and other files from your device.
- **Secure authentication:** User login with salted and hashed password storage for enhanced security.
- **Automatic lockout:** Users are locked out after multiple unsuccessful login attempts.
- **Device identification:** Uploaders are identified by device type and IP address.

---

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Database Reset](#database-reset)
4. [Security](#security)
5. [Dependencies](#dependencies)
6. [Known Issues](#known-issues)
7. [Contributing](#contributing)
8. [License](#license)

---

## Installation

### Prerequisites
- Python 3.x
- `pip` (Python package installer)
- `venv` module for creating virtual environments
- Required binaries: `flask`, `sqlite3`, `curl`, `openssl`

### Automated Installation
1. Clone this repository:
   git clone https://github.com/kleinpanic/iphone-linux-transfer.git 
   cd iphone-linux-transfer
   
2. Run the installation script:
   ./install.sh
   This script will:
   - Check for the `venv` module and attempt installation if missing
   - Check for required binaries and prompt you to install any that are missing
   - Set up a virtual environment and install all Python dependencies
   - Set up an Assets directory so the code can properly work

### Manual Installation
If you'd prefer to install everything manually, follow these steps:

1. Install Python 3.x and `venv`.
2. Create a virtual environment:
   python3 -m venv venv
3. Activate the virtual environment:
   - **Linux/Mac:** `source venv/bin/activate`

4. Install the required Python packages:
   pip install -r requirements.txt
   
---

## Usage
1. **Activate the virtual environment**:
   - **Linux/Mac:** `source venv/bin/activate`
  
2. **Start the application**:
   python app.py
   The application will run on `https://127.0.0.1:5000` by default.

3. **Access the application**:
   - Open your browser and go to `https://127.0.0.1:5000`.

### Available Features
- **Uploading:** Upload links, images, and other files.
- **Downloading:** Download uploaded content.
- **Renaming:** Rename uploaded files.
- **Preview:** Preview uploaded images directly from the app.
- **Delete:** Delete uploaded content.
- Curl: compable with curl ideally. 
  
---

## Database Reset

To start fresh with a new database setup, you can use the reset script provided:

1. Ensure your virtual environment is activated:
   source venv/bin/activate
2. Run the reset script:
   python reset_db.py
   This will:
   - Remove all existing entries from the database
   - Reinitialize the tables for users and uploads

**Note**: Use this command with caution as it will remove all existing data.

---

## Security

- Passwords are salted and hashed before being stored.
- After 3 unsuccessful login attempts, users are locked out, and their IP address is recorded in `locked_ips.txt`.
- To unlock a user, manually remove their IP from `locked_ips.txt`.

---

## Dependencies

This project requires the following:
- **Python Packages** (specified in `requirements.txt`)
  - `Flask`
  - `Werkzeug`
  - Other packages as needed by your project
- **System Binaries**
  - `flask`
  - `sqlite3`
  - `curl`
  - `openssl`

---

## Known Issues

- The application is currently set up for development use. It is not secure for deployment in a production environment.
- Make sure you properly configure your firewall and network settings when using this application on a publicly accessible server.

---

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the repository** on GitHub.
2. **Clone your fork**:
   git clone https://github.com/yourusername/iphone-linux-transfer.git
3. **Create a new branch** for your feature or bug fix:
   git checkout -b feature-name
4. **Make your changes**, commit them, and push to your fork:
   git add .
   git commit -m "Description of your changes"
   git push origin feature-name
5. Open a **Pull Request** on the main repository.

---

## License

This project is licensed under the MIT License. Do whatever the fuck you want with it. 

---

## Support

For any issues or suggestions, please open an issue on the GitHub repository or contact me directly.

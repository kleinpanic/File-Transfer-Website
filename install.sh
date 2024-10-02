#!/bin/bash

# Check for venv installation
check_venv() {
    if ! command -v python3 -m venv &> /dev/null; then
        echo "Python venv is not installed. Attempting to install it..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install python3-venv -y
            elif command -v yum &> /dev/null; then
                sudo yum install python3-venv -y
            else
                echo "Unsupported Linux package manager. Please install Python venv manually."
                exit 1
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # MacOS
            if ! command -v brew &> /dev/null; then
                echo "Homebrew not found. Please install Homebrew from https://brew.sh/"
                exit 1
            fi
            brew install python3
        elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
            # Windows
            echo "Please install Python and add it to your PATH manually."
            exit 1
        else
            echo "Unsupported operating system. Please install Python venv manually."
            exit 1
        fi
    else
        echo "Python venv is already installed."
    fi
}

# Check for required binaries
check_binaries() {
    DEPENDENCIES=("flask" "sqlite3" "curl" "openssl")

    echo "Checking for required dependencies..."
    for dep in "${DEPENDENCIES[@]}"; do
        if ! command -v $dep &> /dev/null; then
            echo "$dep is not installed. Please install it."
            exit 1
        else
            echo "$dep is installed."
        fi
    done
}

# Create virtual environment and install requirements
setup_venv() {
    echo "Setting up virtual environment..."
    python3 -m venv venv

    echo "Activating virtual environment..."
    source venv/bin/activate

    if [[ ! -f "requirements.txt" ]]; then
        echo "requirements.txt not found!"
        deactivate
        exit 1
    fi

    echo "Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "All dependencies installed."

    deactivate
}

# Create assets directory
create_assets_directory() {
    if [[ ! -d "assets" ]]; then
        echo "Creating 'assets' directory..."
        mkdir assets
        echo "'assets' directory created."
    else
        echo "'assets' directory already exists."
    fi
}

# Run the checks and setup
check_venv
check_binaries
setup_venv
create_assets_directory

echo "Installation completed successfully."

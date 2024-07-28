#!/bin/bash

if ! command -v pip &>/dev/null; then
    echo "pip could not be found. Please install pip and try again."
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "python3 could not be found. Please install python3 and try again."
    exit 1
fi

echo "Installing required dependencies, please wait..."

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Please check the error messages above."
    exit 1
fi

echo "Requirements have been installed successfully."
echo "Launching app..."

python3 main.py

if [ $? -ne 0 ]; then
    echo "Failed to launch the app. Please check the error messages above."
    exit 1
fi

echo "App has been launched successfully."
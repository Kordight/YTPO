#!/bin/bash

if ! command -v python3 &>/dev/null; then
    echo "python3 could not be found. Please install python3 and try again."
    exit 1
fi
echo "Launching app..."
python3 main.py

if [ $? -ne 0 ]; then
    echo "Failed to launch the app. Please check the error messages above."
    exit 1
fi

echo "App has been launched successfully."

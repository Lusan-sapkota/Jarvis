#!/bin/bash

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y portaudio19-dev

echo "Installing Python packages..."
pip install -r requirements.txt

# 🗺️ Karnaugh Map Generator

This is a simple Karnaugh Map generator written in Python. It takes a boolean expression and generates a Karnaugh Map for it. It also generates the simplified boolean expression from the Karnaugh Map.

## Usage
Make sure React App is built.
```bash
cd frontend
npm run build
```

Run the server.
```bash
uvicorn main:app --reload
```

## Deployment with Phusion Passenger
```bash
#!/bin/bash

# Remove old repo
rm -rf kmaps

# Make new folder
mkdir kmaps

# Clone repo to server
git clone https://github.com/judahpaul16/kmaps.git

## Install python dependencies
# Create/activate virtual environment
cd kmaps
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Build the app
npm i
npm run build

# Restart Phusion Passenger service
mkdir -p tmp
touch ./tmp/restart.txt
```
--- 

![Screenshot](screenshot.png)

### Live at [kmaps.judahpaul.com](https://kmaps.judahpaul.com/)

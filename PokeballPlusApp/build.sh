#!/bin/bash
# Build the app using pyinstaller
pip install pyinstaller
pyinstaller --windowed --onefile --name PokeballApp main.py
echo "App bundle created in dist/"

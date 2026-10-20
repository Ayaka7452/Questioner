@echo off
cd /d %~dp0
start "" "http://127.0.0.1:8123/index.html?v=%RANDOM%"
python serve.py 2>nul || py serve.py

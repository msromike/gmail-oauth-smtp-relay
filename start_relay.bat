@echo off
REM Start SMTP Relay in minimized window
cd /d "%~dp0"
start /min pythonw smtp_relay.py

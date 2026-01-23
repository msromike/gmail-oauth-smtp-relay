@echo off
REM Start SMTP Relay in system tray
cd /d "%~dp0"
start "" pythonw smtp_relay.py
exit

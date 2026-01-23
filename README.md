# OAuth2 SMTP Relay for Gmail

Local SMTP relay server that accepts email from applications and forwards them to Gmail using OAuth2 authentication.

## Features

- OAuth2 authentication (no password storage required)
- System tray integration with menu controls
- Runs silently in background
- Auto-start support via Windows Startup folder
- Clean logging with rotation support
- Automatic token refresh
- Simple configuration via JSON
- Built for Windows with Python

## Overview

This relay server allows local applications to send email through Gmail without storing passwords. It uses OAuth2 for secure authentication with Google's SMTP servers.

## Architecture

```
Local Application --> SMTP Relay (localhost:1025) --> Gmail SMTP (OAuth2) --> Recipients
```

## Requirements

- Python 3.12+
- Gmail account
- Google Cloud Project with Gmail API enabled
- OAuth2 credentials (Client ID and Client Secret)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/oauth2-smtp-relay.git
cd oauth2-smtp-relay
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Dependencies installed:
- aiosmtpd - SMTP server implementation
- google-auth - OAuth2 authentication
- google-auth-oauthlib - OAuth2 flow handling
- google-auth-httplib2 - HTTP library for Google APIs
- google-api-python-client - Google API client
- pystray - System tray icon support
- Pillow - Image library for tray icon

## Setup

### 1. Google Cloud Configuration

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 Client ID (Web application type)
5. Add authorized redirect URI: `http://localhost:8080/`
6. Add your Gmail address as a test user in OAuth consent screen
7. Download credentials

### 2. Configure Application

Copy the template and edit with your credentials:
```bash
copy config.json.template config.json
```

Edit `config.json`:
- `client_id`: Your OAuth2 client ID
- `client_secret`: Your OAuth2 client secret
- `email`: Your Gmail address

### 3. Authenticate

Run the OAuth2 setup (one-time):
```bash
python setup_oauth.py
```

This will:
- Open your browser for Google authentication
- Save the refresh token to config.json

### 4. Run the Relay

Start the SMTP relay server with system tray:
```bash
start_relay.bat
```

The server will start in the background with a system tray icon.

**System Tray Features**:
- Blue icon appears in system tray
- Right-click menu:
  - View Log (opens in Notepad)
  - Stop & Exit
- No console window (runs silently)

## Configuration

`config.json` settings:

### Gmail Section
- `client_id`: Google OAuth2 client ID
- `client_secret`: Google OAuth2 client secret
- `refresh_token`: OAuth2 refresh token (auto-generated)
- `email`: Your Gmail address

### SMTP Relay Section
- `host`: Relay listen address (default: 127.0.0.1)
- `port`: Relay listen port (default: 1025)
- `gmail_smtp`: Gmail SMTP server (smtp.gmail.com)
- `gmail_smtp_port`: Gmail SMTP port (587)

### Logging Section
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `file`: Log file path

## Usage

Configure applications to use:
- **SMTP Server**: 127.0.0.1
- **Port**: 1025
- **Authentication**: None (relay handles OAuth2)
- **TLS/SSL**: Not required for local connection

## Auto-Start on Login

To make the relay start automatically on login:

1. Press `Win+R` and type `shell:startup`
2. Create a shortcut to `start_relay.bat` in the Startup folder

The relay will start in the system tray automatically when you log in.

## Files

- `setup_oauth.py`: OAuth2 authentication setup (run once)
- `smtp_relay.py`: Main SMTP relay server
- `start_relay.bat`: Windows startup script
- `config.json`: Configuration file
- `smtp_relay.log`: Log file (created on first run)

## Troubleshooting

### Redirect URI Mismatch
Ensure `http://localhost:8080/` is added to authorized redirect URIs in Google Cloud Console.

### Access Denied
Add your Gmail address as a test user in OAuth consent screen settings.

### Token Refresh Failed
Re-run `setup_oauth.py` to generate a new refresh token.

## Security Notes

- OAuth2 tokens stored in config.json
- Keep config.json secure and do not commit to version control
- Relay only accepts connections from localhost (127.0.0.1)
- No password storage required

## Changelog

### 2026-01-23 - Clean Shutdown Handling
- Improved graceful shutdown sequence to eliminate error messages
- Controller stops before event loop for clean termination
- Simplified logging on exit (only success messages, debug for exceptions)
- Tray menu shutdown now shows "SMTP Relay stopped cleanly"

### 2026-01-23 - System Tray Integration
- Added system tray icon with menu (View Log, Stop & Exit)
- Runs silently in background without console window
- Threaded server architecture for non-blocking operation
- Fixed asyncio event loop deprecation warning
- Batch file launches app and exits immediately

### 2026-01-23 - Initial Release
- OAuth2 authentication with Gmail SMTP
- Local SMTP relay server on port 1025
- Simplified logging (startup, auth, email subject only)
- Auto-refresh OAuth2 tokens

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

- Never commit `config.json` or `client_secret*.json` files
- Keep OAuth2 credentials secure
- Relay only accepts localhost connections by default
- Review logs regularly for suspicious activity

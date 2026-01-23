# OAuth2 SMTP Relay for Gmail

Local SMTP relay server that accepts email from applications and forwards them to Gmail using OAuth2 authentication.

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

Dependencies are installed globally:
- aiosmtpd
- google-auth
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client

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

Start the SMTP relay server:
```bash
python smtp_relay.py
```

Or use the batch file:
```bash
start_relay.bat
```

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

A shortcut has been created in:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SMTP_Relay.lnk
```

The relay will start automatically when you log in.

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

### 2026-01-23 - Initial Release
- OAuth2 authentication with Gmail SMTP
- Local SMTP relay server on port 1025
- Automatic startup on Windows login
- Simplified logging (startup, auth, email subject only)
- Auto-refresh OAuth2 tokens

## License

This project is provided as-is for personal use.

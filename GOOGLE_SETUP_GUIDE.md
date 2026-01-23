# Google Cloud OAuth2 Setup Guide

Complete walkthrough for configuring Google Cloud Console for OAuth2 SMTP Relay.

## Overview

This guide walks you through setting up OAuth2 credentials for Gmail SMTP access. The setup is slightly non-standard because we're using OAuth2 for SMTP (not a web app), but Google requires web application credentials.

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project dropdown at the top
3. Click **"New Project"**
4. Enter project name: `SMTP Relay` (or your preference)
5. Click **"Create"**
6. Wait for project creation (notification will appear)

### 2. Enable Gmail API

1. In the left sidebar, go to **"APIs & Services"** → **"Library"**
2. Search for `Gmail API`
3. Click on **"Gmail API"**
4. Click **"Enable"** button
5. Wait for API to be enabled

### 3. Configure OAuth Consent Screen

This is REQUIRED before creating credentials.

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type (even for personal use)
3. Click **"Create"**

**App Information:**
- App name: `SMTP Relay` (or your preference)
- User support email: Select your Gmail address from dropdown
- Developer contact email: Enter your Gmail address

**App Domain (Optional):**
- Leave blank for personal use

4. Click **"Save and Continue"**

**Scopes:**
5. Click **"Add or Remove Scopes"**
6. Find and select: `https://mail.google.com/` (Full Gmail access)
   - You can search for "mail" or scroll to find it
7. Click **"Update"** at bottom
8. Click **"Save and Continue"**

**Test Users (CRITICAL STEP):**
9. Click **"+ Add Users"**
10. Enter YOUR Gmail address (the one you'll send email from)
11. Click **"Add"**
12. Click **"Save and Continue"**

**Summary:**
13. Review and click **"Back to Dashboard"**

> **Important:** Without adding yourself as a test user, authentication will fail with "Access Denied" error.

### 4. Create OAuth2 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** at top
3. Select **"OAuth client ID"**

**Application Type:**
4. Select **"Web application"** from dropdown
   - Yes, web application (even though this is not a web app)
   - This is required for OAuth2 with SMTP

**Name:**
5. Enter name: `SMTP Relay Client` (or your preference)

**Authorized redirect URIs (CRITICAL):**
6. Under "Authorized redirect URIs", click **"+ Add URI"**
7. Enter EXACTLY: `http://localhost:8080/`
   - Must be http (not https)
   - Must be localhost (not 127.0.0.1)
   - Must include port :8080
   - Must end with trailing slash /

8. Click **"Create"**

### 5. Download Credentials

A popup will appear with your credentials:

1. Click **"Download JSON"** button
2. Save the file to your project folder: `c:\bin\OAUTH_SMTP_Relay\`
3. The filename will be: `client_secret_XXXXX.apps.googleusercontent.com.json`
4. Keep this file secure - it contains your client secret

Alternatively:
- Go to **"Credentials"** page
- Find your OAuth 2.0 Client ID in the list
- Click the download icon (⬇) on the right
- Save to project folder

### 6. Note Your Credentials

From the downloaded JSON file, you need:
- `client_id`: Ends with `.apps.googleusercontent.com`
- `client_secret`: Random string

Or view in console:
1. Go to **"Credentials"** page
2. Click on your OAuth 2.0 Client ID name
3. Copy Client ID and Client Secret

### 7. Configure Application

1. Copy the template:
```bash
copy config.json.template config.json
```

2. Edit `config.json`:
```json
{
  "gmail": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "email": "your-email@gmail.com",
    "refresh_token": ""
  }
}
```

3. Replace:
   - `YOUR_CLIENT_ID` with your actual client ID
   - `YOUR_CLIENT_SECRET` with your actual client secret
   - `your-email@gmail.com` with your Gmail address

### 8. Run OAuth2 Setup

1. Open terminal in project folder
2. Run:
```bash
python setup_oauth.py
```

3. Your browser will open automatically
4. Log in to your Gmail account
5. You'll see a warning: "Google hasn't verified this app"
   - Click **"Continue"** (or **"Advanced"** → **"Go to SMTP Relay (unsafe)"**)
6. Grant permissions to access Gmail
7. You'll see "The authentication flow has completed"
8. Return to terminal - it will show success message

The `refresh_token` is now saved in `config.json`.

### 9. Test the Relay

Start the relay:
```bash
start_relay.bat
```

The system tray icon should appear. Send a test email from any local application to verify.

## Troubleshooting

### "Redirect URI Mismatch"
- Verify you added `http://localhost:8080/` exactly in Google Console
- Check for typos (http not https, localhost not 127.0.0.1, trailing slash)

### "Access Denied" Error
- Add your Gmail address as a test user in OAuth consent screen
- Wait a few minutes for changes to propagate

### "Invalid Client"
- Verify client_id and client_secret are correct in config.json
- Check for extra spaces or quotes

### Browser Doesn't Open
- Manually copy the URL from terminal and paste in browser
- Check firewall isn't blocking port 8080

## Security Notes

**Keep These Files Secret:**
- `config.json` - Contains refresh token
- `client_secret_*.json` - Contains client secret

**Safe to Share:**
- Client ID (ends with .apps.googleusercontent.com)
- Application name
- Redirect URI

**Publishing Status:**
- Your app stays in "Testing" status
- Only test users (you) can authenticate
- This is perfect for personal use
- No need to verify app or publish

## Why Web Application Type?

Google requires "Web application" OAuth2 client type for:
- Desktop applications using OAuth2
- Applications with local redirect (localhost)
- SMTP/IMAP OAuth2 authentication

The "Desktop app" type doesn't support the authentication flow needed for SMTP.

## Refresh Token Lifetime

- Refresh tokens for testing apps don't expire
- As long as you're a test user, the token remains valid
- If you remove yourself as test user, re-run setup_oauth.py

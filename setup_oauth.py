#!/usr/bin/env python3
"""
OAuth2 Setup Script for Gmail SMTP Relay
Run this once to generate and save OAuth2 credentials
"""

import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

# Gmail SMTP scope
SCOPES = ['https://mail.google.com/']

def setup_oauth():
    """Setup OAuth2 credentials for Gmail SMTP"""
    
    config_path = Path(__file__).parent / 'config.json'
    
    # Check if config exists
    if not config_path.exists():
        print("[ERROR] config.json not found!")
        print("[INFO] Copy config.json.template to config.json and fill in your client_id and client_secret")
        print("\nTo get credentials:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create a project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 Client ID (Desktop application)")
        print("5. Download credentials and copy client_id & client_secret to config.json")
        return False
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    client_id = config['gmail']['client_id']
    client_secret = config['gmail']['client_secret']
    
    if 'YOUR_CLIENT_ID' in client_id or not client_id:
        print("[ERROR] Please update config.json with your actual client_id and client_secret")
        return False
    
    print("[AUTH] Starting OAuth2 authentication flow...")
    print("[INFO] Your browser will open for Google authentication")
    
    # Create client config for OAuth flow (works with both web and desktop apps)
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/", "http://localhost:8080"]
        }
    }
    
    print(f"[INFO] Using redirect URI: http://localhost:8080/")
    print(f"[INFO] Make sure this EXACT URI is in Google Cloud Console -> Credentials -> Your OAuth Client -> Authorized redirect URIs")
    print()
    
    # Run OAuth flow
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=8080, open_browser=True)
    
    # Save refresh token to config
    config['gmail']['refresh_token'] = creds.refresh_token
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("[OK] OAuth2 setup complete!")
    print(f"[OK] Refresh token saved to {config_path}")
    print("\n[START] You can now run smtp_relay.py")
    return True

if __name__ == '__main__':
    setup_oauth()

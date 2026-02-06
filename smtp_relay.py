#!/usr/bin/env python3
"""
OAuth2 SMTP Relay for Gmail
Accepts emails from local applications and forwards them to Gmail using OAuth2
"""

import asyncio
import json
import logging
import smtplib
import sys
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPServer
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pystray
from PIL import Image, ImageDraw

class GmailOAuth2Handler:
    """Handler for SMTP relay with OAuth2 Gmail authentication"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('GmailOAuth2Handler')
        self.credentials = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load and refresh OAuth2 credentials"""
        try:
            gmail_config = self.config['gmail']
            
            # Create credentials from config
            self.credentials = Credentials(
                token=None,
                refresh_token=gmail_config['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=gmail_config['client_id'],
                client_secret=gmail_config['client_secret'],
                scopes=['https://mail.google.com/']
            )
            
            # Refresh the token
            self.credentials.refresh(Request())
            self.logger.info("OAuth2 authenticated")
            
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            self.credentials = None
    
    def _get_oauth2_string(self):
        """Generate OAuth2 authentication string for SMTP"""
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        
        access_token = self.credentials.token
        # OAuth2 format: base64(user=USERNAME\1auth=Bearer ACCESS_TOKEN\1\1)
        import base64
        auth_string = f"user={self.config['gmail']['email']}\1auth=Bearer {access_token}\1\1"
        return base64.b64encode(auth_string.encode()).decode()
    
    async def handle_DATA(self, server, session, envelope):
        """Handle incoming email data"""
        try:
            # Extract subject from email content
            from email import message_from_bytes
            msg = message_from_bytes(envelope.content)
            subject = msg.get('Subject', '(no subject)')
            
            self.logger.info(f"Sending: From={envelope.mail_from} Subject='{subject}'")
            
            # Send via Gmail SMTP with OAuth2
            self._send_via_gmail(envelope)
            return '250 Message accepted for delivery'
            
        except Exception as e:
            self.logger.error(f"Failed to forward email: {e}")
            return '451 Requested action aborted: error in processing'
    
    def _send_via_gmail(self, envelope):
        """Send email via Gmail SMTP using OAuth2"""
        import subprocess
        
        try:
            # Check if credentials exist
            if not self.credentials:
                raise Exception("OAuth credentials not loaded. Run setup_oauth.py")
            
            # Refresh credentials if needed
            if not self.credentials.valid:
                self.credentials.refresh(Request())
            
            # Connect to Gmail SMTP
            smtp_config = self.config['smtp_relay']
            server = smtplib.SMTP(smtp_config['gmail_smtp'], smtp_config['gmail_smtp_port'])
            server.starttls()
            
            # Authenticate with OAuth2
            auth_string = self._get_oauth2_string()
            server.docmd('AUTH', 'XOAUTH2 ' + auth_string)
            
            # Send the email
            server.sendmail(
                envelope.mail_from,
                envelope.rcpt_tos,
                envelope.content.decode('utf-8', errors='replace')
            )
            
            server.quit()
            
        except Exception as e:
            error_str = str(e)
            # Check if it's an OAuth error
            if 'invalid_grant' in error_str or 'expired' in error_str.lower() or 'revoked' in error_str.lower():
                msg_text = "SMTP Relay: OAuth token expired. Run setup_oauth.py to refresh."
                self.logger.error(msg_text)
                try:
                    subprocess.run(['msg', '*', msg_text], timeout=5)
                except:
                    pass
            raise

class SMTPRelayServer:
    """Main SMTP Relay Server"""
    
    def __init__(self, config_path='config.json'):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._setup_logging()
        self.controller = None
        self.tray_icon = None
        self.running = False
        self.loop = None
        
    def _load_config(self):
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            print(f"❌ Config file not found: {self.config_path}")
            print("📝 Run setup_oauth.py first to configure OAuth2")
            sys.exit(1)
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'smtp_relay.log')
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # Silence noisy aiosmtpd logging
        logging.getLogger('mail.log').setLevel(logging.WARNING)
        
        self.logger = logging.getLogger('SMTPRelayServer')
    
    def _create_tray_icon(self):
        """Create system tray icon"""
        # Create a simple icon
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem('SMTP Relay Running', lambda: None, enabled=False),
            pystray.MenuItem('View Log', self._view_log),
            pystray.MenuItem('Stop & Exit', self._quit_app)
        )
        
        self.tray_icon = pystray.Icon('smtp_relay', image, 'SMTP Relay', menu)
    
    def _view_log(self):
        """Open log file"""
        import subprocess
        log_file = self.config.get('logging', {}).get('file', 'smtp_relay.log')
        log_path = Path(__file__).parent / log_file
        if log_path.exists():
            subprocess.Popen(['notepad.exe', str(log_path)])
    
    def _quit_app(self):
        """Stop the server and exit"""
        self.logger.info("Shutting down from tray menu")
        self.running = False
        # Stop controller first
        if self.controller:
            try:
                self.controller.stop()
                self.logger.info("SMTP Relay stopped cleanly")
            except Exception as e:
                self.logger.debug(f"Controller stop: {e}")
        # Then stop event loop
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        # Finally stop tray
        if self.tray_icon:
            self.tray_icon.stop()
    
    def _run_server(self, handler):
        """Run the SMTP server in background thread"""
        relay_config = self.config['smtp_relay']
        host = relay_config['host']
        port = relay_config['port']
        
        self.logger.info(f"SMTP Relay starting on {host}:{port}")
        
        # Create and start controller
        self.controller = Controller(
            handler,
            hostname=host,
            port=port
        )
        
        self.controller.start()
        self.running = True
        
        # Keep running
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            while self.running:
                self.loop.run_until_complete(asyncio.sleep(1))
        except Exception as e:
            if self.running:  # Only log if unexpected
                self.logger.error(f"Server error: {e}")
    
    def start(self):
        """Start the SMTP relay server with system tray"""
        # Create handler (continues even if credentials fail to load)
        handler = GmailOAuth2Handler(self.config)
        
        # Start server in background thread
        server_thread = threading.Thread(target=self._run_server, args=(handler,), daemon=True)
        server_thread.start()
        
        # Create and run tray icon (blocks until quit)
        self._create_tray_icon()
        self.tray_icon.run()
    
    def stop(self):
        """Stop the SMTP relay server (for backward compatibility)"""
        self._quit_app()

def main():
    """Main entry point"""
    config_file = Path(__file__).parent / 'config.json'
    server = SMTPRelayServer(config_file)
    server.start()

if __name__ == '__main__':
    main()

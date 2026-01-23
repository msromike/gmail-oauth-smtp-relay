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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPServer
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

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
            raise
    
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

class SMTPRelayServer:
    """Main SMTP Relay Server"""
    
    def __init__(self, config_path='config.json'):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._setup_logging()
        self.controller = None
        
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
    
    def start(self):
        """Start the SMTP relay server"""
        relay_config = self.config['smtp_relay']
        host = relay_config['host']
        port = relay_config['port']
        
        self.logger.info(f"SMTP Relay starting on {host}:{port}")
        
        # Create handler
        handler = GmailOAuth2Handler(self.config)
        
        # Create and start controller
        self.controller = Controller(
            handler,
            hostname=host,
            port=port
        )
        
        self.controller.start()
        
        # Keep running
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the SMTP relay server"""
        if self.controller:
            self.controller.stop()
            self.logger.info("SMTP Relay stopped")

def main():
    """Main entry point"""
    config_file = Path(__file__).parent / 'config.json'
    server = SMTPRelayServer(config_file)
    server.start()

if __name__ == '__main__':
    main()

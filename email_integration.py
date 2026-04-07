"""
Real Email Integration Module
Connects to Gmail or Outlook to process actual emails
"""

import os
import base64
from typing import List, Optional
from abc import ABC, abstractmethod

# For Gmail
try:
    from google.auth.transport.requests import Request  # type: ignore
    from google.oauth2.credentials import Credentials  # type: ignore
    from google.auth.oauthlib.flow import InstalledAppFlow  # type: ignore
    from google.api_core.exceptions import GoogleAPIError  # type: ignore
    import google.auth  # type: ignore
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

# For Outlook
try:
    import requests
    from msal import PublicClientApplication
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False

from env.models import Email, EmailPriority, EmailCategory
from datetime import datetime


class EmailProvider(ABC):
    """Abstract base class for email providers"""

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def fetch_emails(self, limit: int = 10) -> List[Email]:
        pass

    @abstractmethod
    def send_reply(self, message_id: str, reply_text: str) -> bool:
        pass


class GmailProvider(EmailProvider):
    """Gmail API Integration"""

    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, credentials_file: str = 'gmail_credentials.json'):
        if not GMAIL_AVAILABLE:
            raise ImportError("Google Auth libraries not installed. Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        
        self.credentials_file = credentials_file
        self.service = None
        self.creds = None

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Check if we have cached credentials
        if os.path.exists('token.pickle'):
            import pickle
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found: {self.credentials_file}\n"
                        "1. Go to Google Cloud Console: https://console.cloud.google.com\n"
                        "2. Create OAuth 2.0 credentials (Desktop app)\n"
                        "3. Download and save as 'gmail_credentials.json'"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            import pickle
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.creds = creds
        from googleapiclient.discovery import build
        self.service = build('gmail', 'v1', credentials=creds)
        print("[OK] Gmail authentication successful!")

    def fetch_emails(self, limit: int = 10) -> List[Email]:
        """Fetch emails from Gmail inbox"""
        if not self.service:
            self.authenticate()

        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=limit
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me', id=msg['id'], format='full'
                ).execute()

                email = self._parse_gmail_message(msg_data)
                emails.append(email)

            print(f"[OK] Fetched {len(emails)} unread emails from Gmail")
            return emails

        except GoogleAPIError as e:
            print(f"[ERROR] Gmail API error: {e}")
            return []

    def send_reply(self, message_id: str, reply_text: str) -> bool:
        """Send a reply to an email"""
        try:
            # Get original message
            msg = self.service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()

            # Extract sender
            headers = msg['payload']['headers']
            from_addr = next(h['value'] for h in headers if h['name'] == 'From')
            subject = next(h['value'] for h in headers if h['name'] == 'Subject')
            original_id = next(h['value'] for h in headers if h['name'] == 'Message-ID')

            # Create reply
            reply_subject = f"Re: {subject}" if not subject.startswith('Re:') else subject
            reply_body = f"{reply_text}\n\nOn {datetime.now().strftime('%a, %b %d, %Y at %I:%M %p')}, {from_addr} wrote:"

            # Send via SMTP (requires additional setup)
            print(f"[INFO] Reply ready to send (manual SMTP setup required): {reply_subject}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to send reply: {e}")
            return False

    def _parse_gmail_message(self, msg_data: dict) -> Email:
        """Parse Gmail message into Email model"""
        headers = msg_data['payload']['headers']
        
        def get_header(name):
            return next((h['value'] for h in headers if h['name'] == name), '')

        sender = get_header('From')
        subject = get_header('Subject')
        date_str = get_header('Date')

        # Extract body
        body = ''
        if 'parts' in msg_data['payload']:
            for part in msg_data['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        else:
            if 'data' in msg_data['payload']['body']:
                body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode('utf-8')

        # Parse category using simple heuristics
        category = self._categorize_email(subject, body)

        return Email(
            from_addr=sender,
            subject=subject,
            body=body[:500],  # Limit body size
            category=category,
            priority=EmailPriority.MEDIUM,
            timestamp=datetime.now(),
            email_id=msg_data['id']
        )

    def _categorize_email(self, subject: str, body: str) -> EmailCategory:
        """Categorize email based on content"""
        text = (subject + " " + body).lower()

        if any(word in text for word in ['spam', 'unsubscribe', 'promotional', 'offer']):
            return EmailCategory.SPAM
        elif any(word in text for word in ['invoice', 'payment', 'charge', 'bill']):
            return EmailCategory.BILLING
        elif any(word in text for word in ['feedback', 'review', 'suggestion']):
            return EmailCategory.FEEDBACK
        elif any(word in text for word in ['support', 'help', 'issue', 'problem']):
            return EmailCategory.SUPPORT
        else:
            return EmailCategory.PRODUCT


class OutlookProvider(EmailProvider):
    """Outlook/Microsoft Graph API Integration"""

    def __init__(self, client_id: str, tenant: str = 'common'):
        if not OUTLOOK_AVAILABLE:
            raise ImportError("Requests and MSAL libraries not installed. Run: pip install requests msal")

        self.client_id = client_id
        self.tenant = tenant
        self.app = PublicClientApplication(client_id, authority=f'https://login.microsoftonline.com/{tenant}')
        self.access_token = None

    def authenticate(self):
        """Authenticate with Microsoft Graph API"""
        scopes = ['https://graph.microsoft.com/.default']

        result = self.app.acquire_token_interactive(scopes=scopes)

        if 'access_token' in result:
            self.access_token = result['access_token']
            print("[OK] Outlook authentication successful!")
        else:
            raise Exception(f"Authentication failed: {result.get('error_description')}")

    def fetch_emails(self, limit: int = 10) -> List[Email]:
        """Fetch emails from Outlook inbox"""
        if not self.access_token:
            self.authenticate()

        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            url = f'https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messages?$top={limit}&$filter=isRead eq false'

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            messages = response.json().get('value', [])
            emails = []

            for msg in messages:
                email = self._parse_outlook_message(msg)
                emails.append(email)

            print(f"[OK] Fetched {len(emails)} unread emails from Outlook")
            return emails

        except requests.RequestException as e:
            print(f"[ERROR] Outlook API error: {e}")
            return []

    def send_reply(self, message_id: str, reply_text: str) -> bool:
        """Send a reply to an email"""
        if not self.access_token:
            self.authenticate()

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            body = {
                'message': {
                    'body': {
                        'contentType': 'text',
                        'content': reply_text
                    }
                }
            }

            url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}/reply'
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()

            print(f"[OK] Reply sent successfully")
            return True

        except requests.RequestException as e:
            print(f"[ERROR] Failed to send reply: {e}")
            return False

    def _parse_outlook_message(self, msg_data: dict) -> Email:
        """Parse Outlook message into Email model"""
        sender = msg_data['from']['emailAddress']['address']
        subject = msg_data['subject']
        body = msg_data['bodyPreview']
        received_time = msg_data['receivedDateTime']

        category = self._categorize_email(subject, body)

        return Email(
            from_addr=sender,
            subject=subject,
            body=body[:500],
            category=category,
            priority=EmailPriority.MEDIUM,
            timestamp=datetime.fromisoformat(received_time.replace('Z', '+00:00')),
            email_id=msg_data['id']
        )

    def _categorize_email(self, subject: str, body: str) -> EmailCategory:
        """Categorize email based on content"""
        text = (subject + " " + body).lower()

        if any(word in text for word in ['spam', 'unsubscribe', 'promotional']):
            return EmailCategory.SPAM
        elif any(word in text for word in ['invoice', 'payment', 'bill']):
            return EmailCategory.BILLING
        elif any(word in text for word in ['feedback', 'review']):
            return EmailCategory.FEEDBACK
        elif any(word in text for word in ['support', 'help', 'issue']):
            return EmailCategory.SUPPORT
        else:
            return EmailCategory.PRODUCT


def get_email_provider(provider: str = 'gmail', **kwargs) -> EmailProvider:
    """Factory function to get email provider"""
    if provider.lower() == 'gmail':
        return GmailProvider(**kwargs)
    elif provider.lower() == 'outlook':
        return OutlookProvider(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")

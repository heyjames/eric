import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def create_message(to, subject, body):
    # Create a MIME message
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    return raw_message

def initialize_credentials():
    # Set up the Gmail API
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None

    if os.path.exists('../token.json'):
        creds = Credentials.from_authorized_user_file('../token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('../token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def send_message(email):
    creds = initialize_credentials()
    # Set up the Gmail service
    service = build('gmail', 'v1', credentials=creds)

    raw_message = create_message(email['to'], email['subject'], email['body'])
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
    
    print('Email sent successfully!')

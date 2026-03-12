import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import Optional

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.service = None
        self.initialized = False
        self._authenticate()

    def _authenticate(self):
        creds = None
        token_path = 'token.json'
        creds_path = 'credentials.json'

        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception:
                pass

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    pass
            elif os.path.exists(creds_path):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                    # In a server environment, this flow is tricky without a UI. 
                    # We'll assume for now the user sets this up locally or we use a service account.
                    # For this demo, we'll skip interactive login if it fails.
                    pass 
                except Exception:
                    pass
        
        if creds and creds.valid:
            try:
                self.service = build('calendar', 'v3', credentials=creds)
                self.initialized = True
                print("Google Calendar initialized.")
            except Exception as e:
                print(f"Error building calendar service: {e}")
        else:
            print("Warning: Google Calendar credentials not valid or found. Running in mock mode.")

    def create_event(self, summary: str, start_time: str, end_time: str, description: str = "") -> str:
        if not self.initialized:
            return f"Mock: Event '{summary}' created in Google Calendar for {start_time}."

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time, # ISO format '2023-05-28T09:00:00-07:00'
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return f"Event created: {event.get('htmlLink')}"
        except Exception as e:
            return f"Error creating calendar event: {str(e)}"

calendar_service = CalendarService()

# calendar_helper.py

import datetime
import pytz
import tempfile
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/calendar']

calendar_config = {
    "calendar_id": None,
    "service_account_json": None
}

def init_calendar_config(json_data, calendar_id):
    calendar_config["calendar_id"] = calendar_id
    calendar_config["service_account_json"] = json_data

def get_calendar_service():
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp:
        tmp.write(calendar_config["service_account_json"])
        tmp_path = tmp.name

    credentials = service_account.Credentials.from_service_account_file(
        tmp_path, scopes=SCOPES)
    return build('calendar', 'v3', credentials=credentials)

def create_event(task_text, due_date, description=None):
    try:
        service = get_calendar_service()

        due_datetime = datetime.datetime.strptime(due_date, "%Y-%m-%d").replace(hour=9)
        timezone = pytz.timezone("Asia/Kolkata")
        due_datetime = timezone.localize(due_datetime)

        event = {
            'summary': task_text,
            'description': description or '',
            'start': {
                'dateTime': due_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': (due_datetime + datetime.timedelta(hours=1)).isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},
                    {'method': 'email', 'minutes': 30},
                ],
            },
        }

        created_event = service.events().insert(calendarId=calendar_config["calendar_id"], body=event).execute()
        return created_event
    except Exception as e:
        print(f"❌ Failed to create calendar event: {e}")
        return None

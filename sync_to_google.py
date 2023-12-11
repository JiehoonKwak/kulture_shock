import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()
cal_id = os.getenv('cal_id')
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDS_FILE = '/Users/jiehoonk/miniconda3/envs/project/script/kulture_shock/client_secret_710606849202-9h4k3kp86aldmpr9f9enqa3284dkjcod.apps.googleusercontent.com.json'
TOKEN_FILE = '/Users/jiehoonk/miniconda3/envs/project/script/kulture_shock/token.json'


def get_authenticated_service(credentials_file, scopes, token_file):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
        creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def event_builder(row):
    event = {
        'summary': row[1],
        'location': row[2],
        'start': {
            'dateTime': row[0]+ 'T19:00:00',
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': row[0] + 'T22:00:00',
            'timeZone': 'Asia/Seoul',
        },
    }
    return event

def sync():
    service = get_authenticated_service(CREDS_FILE, SCOPES, TOKEN_FILE)
    json_files = [f for f in os.listdir(os.getcwd()) if f.endswith('.json')]
    json_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
    file = os.path.join(os.getcwd(),json_files[0])

    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for entry in data:
            event = event_builder(entry)
            execute = service.events().insert(calendarId='cal_id', body=event).execute()

if __name__ == '__main__':
    service = get_authenticated_service(CREDS_FILE, SCOPES, TOKEN_FILE)

    json_files = [f for f in os.listdir(os.getcwd()) if f.endswith('.json') and f.startswith('concert')]
    json_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
    file = os.path.join(os.getcwd(),json_files[0])
    print(f"***** File name being processed is... : {file} *****")

    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for entry in data:
            event = event_builder(entry)
            execute = service.events().insert(calendarId='cal_id', body=event).execute()
    print("**** Succeeded syncing with Google Calendar")

 


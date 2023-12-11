#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
from dotenv import load_dotenv


load_dotenv()
bot_token = os.getenv('bot_token')
chat_id = os.getenv('chat_id')
username = os.getenv('username')
password = os.getenv('password')



def load_data(path):
    try:
        with open(path, 'r', encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def scrape_concert_data():
    login_url = "https://admin.kultureshock.net/login.php?goto=en_concerts.php"

    session = requests.Session()
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    login_form = soup.find('form', {'name': 'login'})
    form_userid_name = login_form.find('input', {'name': 'form_userid'})['name']
    form_password_name = login_form.find('input', {'name': 'form_password'})['name']
    form_action_value = login_form.find('input', {'name': 'form_action'})['value']
    login_data = {
        form_userid_name: username,
        form_password_name: password,
        'form_action': form_action_value,
    }
    response = session.post(login_url, data=login_data)

    concert_page_url = "https://admin.kultureshock.net/en_concerts.php"
    concert_page = session.get(concert_page_url)
    soup = BeautifulSoup(concert_page.text, 'html.parser')

    rows = soup.select('tr[bgcolor]')

    new_data = []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 4:
            date_elem = cells[1].find('b')
            title_elem = cells[2]
            venue_elem = cells[3]

            # Check if any of the elements are None or contain "N/A"
            if date_elem and title_elem and venue_elem:
                date = date_elem.text.strip()
                parsed_date = datetime.strptime(date, '%b-%d-%Y')
                formatted_date = parsed_date.strftime('%Y-%m-%d')
                title = title_elem.text.strip()
                venue = venue_elem.text.strip()

                # Only add data if none of them are "N/A"
                if date != "N/A" and title != "N/A" and venue != "N/A":
                    new_data.append([formatted_date, title, venue])

    return new_data

if __name__ == '__main__':
    now = datetime.now()
    message_time = datetime.now().strftime("%m/%d %H:%M")
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    
    existing_data = load_data('/Users/jiehoonk/miniconda3/envs/project/script/kulture_shock/calendar_data.json') 
    new_data = scrape_concert_data()
    future_events = [event for event in new_data if datetime.strptime(event[0], '%Y-%m-%d') >= now]
    new_added = []
    
    for entry in new_data:
        if entry not in existing_data:
            new_added.append(entry)
    
    if new_added:
        existing_data.extend(new_added)
        save_data(existing_data, '/Users/jiehoonk/miniconda3/envs/project/script/kulture_shock/calendar_data.json')
        
        new_filename = f'/Users/jiehoonk/miniconda3/envs/project/script/kulture_shock/concert_data_{current_datetime}.json'
        save_data(new_added, new_filename)
        
        message = f"{message_time} : Updated data saved to {new_filename}. Check on Mac"

    else:
        message = f"{message_time} : Nothing to update"
            
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}'
    response = requests.get(url)





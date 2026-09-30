import json
import requests
from ics import Calendar, Event
from datetime import datetime
import pytz

# Match Node.js endpoints
MASTRA_URL = "http://127.0.0.1:8000/describe"
PROCESS_DATA_URL = "http://127.0.0.1:8000/process_data"
STORED_DATA_URL = "http://127.0.0.1:8000/stored_data"

def get_mastra_description(text):
    payload = {"text": text}
    response = requests.post(MASTRA_URL, json=payload)
    if response.ok:
        return response.json().get("description", "")
    return ""

def send_to_server(data):
    try:
        response = requests.post(PROCESS_DATA_URL, json=data)
        if response.ok:
            return response.json()  # expects { "result": { ... } }
        else:
            print(f"Server error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def fetch_stored_data():
    try:
        response = requests.get(STORED_DATA_URL)
        if response.ok:
            return response.json().get("stored", [])
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch stored data: {e}")
        return []

def put_into_eastern(date_string):
    naive_date = datetime.strptime(date_string, "%Y-%m-%d").replace(year=2025)
    eastern = pytz.timezone("US/Eastern")
    return eastern.localize(naive_date)

def text_to_json(text, link):
    # Build initial event JSON
    ev = {
        "title": "Club Event",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "links": [link],
        "description": get_mastra_description(text),
        "original_text": text,
        "created_at": datetime.now().isoformat()
    }
    
    # Send to server
    server_response = send_to_server(ev)
    
    if server_response and "result" in server_response:
        processed_ev = server_response["result"]
        print("Data processed by server")
    else:
        processed_ev = ev
        print("⚠️ Using original data (server processing failed)")
    
    # Save locally
    with open("club.json", "w") as f:
        json.dump(processed_ev, f, indent=2)
    
    return processed_ev

def create_ics(event_json, ics_number):
    c = Calendar()
    e = Event()
    e.name = event_json["title"]
    e.begin = put_into_eastern(event_json["date"])
    e.description = event_json["description"] + "\n\nLinks:\n"
    for link in event_json["links"]:
        e.description += link + "\n"
    c.events.add(e)
    with open(f"event{ics_number}.ics", "w") as f:
        f.writelines(c)
    return f

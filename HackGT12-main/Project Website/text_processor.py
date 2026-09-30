from image_processor import *
from openai import OpenAI
from ics import Calendar, Event
from datetime import datetime
import json
import pytz

def put_into_eastern(date_string):
    naive_date = datetime.strptime(date_string, "%Y-%m-%d").replace(year = 2025)
    eastern = pytz.timezone("US/Eastern")
    eastern_date = eastern.localize(naive_date)
    return eastern_date

def retrieve_text(file_name):
    img = load_image(file_name)
    link = detect_qr_code(img)
    page_content = get_html_content(link)
    text = get_text(page_content)

    return text, link

def text_to_json(text):
    client = OpenAI(api_key="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")

    response = client.chat.completions.create(
        model="gpt-4o",   # You can use gpt-4o, gpt-4.1, or gpt-3.5-turbo too
        messages=[ 
            {"role": "system", "content": f"You will be given text about an event, make a JSON dictionary with 'title', 'date', 'links', and 'description' as keys. Title will be a string that is the name of the event/organization, or a very brief description. Be very careful to have a good title. For sites like forms or invitations, make sure the title reflects what the form is for or what the user is invited to. Date is the callout/interest meeting/application date/time, if present. If date is not clearly present in the text, use today's date {datetime.now()} at midnight. Date is STRICLY a date only, no other text, just the date in usable form. Ensure the year in the date is in an appropriate year (current or approaching, as appropriate).Make sure the time is in Eastern time. Links is a list of links found on the page, as a Python list. Description is a short description of the event/organization. Output ONLY the JSON text in a code block, nothing else."},
            {"role": "user", "content": text}
        ],
    )
    
    return response.choices[0].message.content

def create_ics(json_text, ics_number, link):
    start_index = json_text.index("{")
    end_index = json_text.index("}")

    json_input = json_text[start_index : end_index + 1]

    ev = json.loads(json_input)

    c = Calendar()
    e = Event()

    e.name = ev['title']
    e.begin = put_into_eastern(ev['date'])
    e.description = ev['description'] + "\n\n Links: "
    for link in [link] + ev['links']:
        e.description += link + "\n"
    
    c.events.add(e)

    with open("event" + str(ics_number) + ".ics", "w") as f:
        f.writelines(c)
    return f

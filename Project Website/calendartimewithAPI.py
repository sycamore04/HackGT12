!pip install -q -U google-genai
import re
from ics import Calendar, Event
from datetime import datetime
import pytz



def create_calendar():
    return Calendar()

def add_event(calendar, title, start_time, end_time, location="", description=""):
    event = Event()
    event.name = title
    event.begin = start_time
    event.end = end_time
    event.location = location
    event.description = description
    calendar.events.add(event)

def save_calendar(calendar, filename="events.ics"):
    with open(filename, "w") as f:
        f.writelines(calendar.serialize_iter())



def parse_datetime(text):

    match = re.search(r"(\w+\s\d{1,2},\s\d{4})\s(\d{1,2}:\d{2}\s[APM]{2})\s-\s(\d{1,2}:\d{2}\s[APM]{2})", text)
    if match:
        date_str = match.group(1)
        start_str = match.group(2)
        end_str = match.group(3)
        start = datetime.strptime(f"{date_str} {start_str}", "%b %d, %Y %I:%M %p")
        end = datetime.strptime(f"{date_str} {end_str}", "%b %d, %Y %I:%M %p")
        return start, end
    return None, None

def parse_event_data(extracted_text, timezone_str='UTC'):
    date_part_pattern = r"([A-Za-z]{3,9}\s\d{1,2}(?:st|nd|rd|th)?,\s\d{4})"
    date_match = re.search(date_part_pattern, extracted_text)

    start = None
    end = None
    title = "Untitled Event"
    location = ""
    description = extracted_text

    try:
        target_timezone = pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        print(f"Warning: Unknown timezone '{timezone_str}'. Using UTC instead.")
        target_timezone = pytz.UTC


    if date_match:
        date_part = date_match.group(1)
        date_part_cleaned = re.sub(r"(st|nd|rd|th),", ",", date_part)

        text_after_date = extracted_text[date_match.end():].strip()
        
        time_range_pattern = r"(\d{1,2}(?::\d{2})?[ap]m)\s?-\s?(\d{1,2}(?::\d{2})?[ap]m)"
        time_range_match = re.search(time_range_pattern, text_after_date, re.IGNORECASE) # Ignore case for am/pm

        if time_range_match:
            start_time_str = time_range_match.group(1)
            end_time_str = time_range_match.group(2)
            time_formats_to_try = ["%I%p", "%I %p", "%I:%M%p", "%I:%M %p"]

            for time_format in time_formats_to_try:
                try:
                    naive_start = datetime.strptime(f"{date_part_cleaned} {start_time_str.strip()}", f"%b %d, %Y {time_format}")
                    naive_end = datetime.strptime(f"{date_part_cleaned} {end_time_str.strip()}", f"%b %d, %Y {time_format}")

                    start = target_timezone.localize(naive_start)
                    end = target_timezone.localize(naive_end)
                    break
                except ValueError:
                     try: 
                        naive_start = datetime.strptime(f"{date_part_cleaned} {start_time_str.strip()}", f"%B %d, %Y {time_format}")
                        naive_end = datetime.strptime(f"{date_part_cleaned} {end_time_str.strip()}", f"%B %d, %Y {time_format}")
                        
                        start = target_timezone.localize(naive_start)
                        end = target_timezone.localize(naive_end)
                        break 
                     except ValueError:
                        continue 


            if start and end:
                before_date = extracted_text[:date_match.start()].strip()
                after_time_range = text_after_date[time_range_match.end():].strip()

                title = before_date if before_date else "Untitled Event"

                location = ""
                description = ""

                after_lower = after_time_range.lower()
                at_index = after_lower.find(" at ")
                about_index = after_lower.find(" about ")

                if at_index != -1:
                    description = after_time_range[:at_index].strip()

               
                    if about_index != -1 and about_index > at_index:
                       
                        location = after_time_range[at_index + len(" at "):about_index].strip()
                      
                        description = (description + " " + after_time_range[about_index + len(" about "):].strip()).strip()
                    else:
                      
                        location = after_time_range[at_index + len(" at "):].strip()
                

                elif about_index != -1:
                  
                    description = after_time_range[about_index + len(" about "):].strip()
                  
                    description = (after_time_range[:about_index].strip() + " " + description).strip()
                else:
                  
                    description = after_time_range.strip()
                description = description.strip()


    return title, start, end, location, description


from google.colab import userdata

api_key = userdata.get('hackgt12')

from google.colab import drive
drive.mount('/content/drive')

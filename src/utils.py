from datetime import datetime
import json
import pytz
import requests
import re
import time
from urllib.parse import urlparse

def get_unix_time():
    return int(time.time())

def get_iso_time():
    current_utc_time = datetime.utcnow()

    utc_timezone = pytz.timezone('UTC')

    current_utc_time = current_utc_time.replace(tzinfo=utc_timezone)

    # Format as ISO 8601 string
    iso_format_utc = current_utc_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return iso_format_utc

def convert_iso_time_to_human_readable(iso_string):
    # Parse ISO string to datetime dictionary in UTC
    utc_datetime = datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)

    # Convert to local time
    local_timezone = pytz.timezone('America/Los_Angeles')
    local_datetime = utc_datetime.astimezone(local_timezone)

    # Format as human-readable date with 24-hour time
    formatted_time = local_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")

    return formatted_time
    # print(f"ISO time: {iso_string}")
    # print(f"Local time: {formatted_time}")

# Extract URLs from given text using regular expression
def extract_urls(text):
    urls = []

    try:
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        found_urls = url_pattern.findall(text)

        urls.extend(found_urls)
    except Exception as e:
        print(f'Error: {str(e)}')

    return urls

# Extract Zoom registration URLs from given text using regular expression
def extract_zoom_registration_link(text):
    urls = []

    try:
        url_pattern = re.compile(r'https?://alamedaca-gov\.zoom\.us/webinar/register/\S+')
        found_urls = url_pattern.findall(text)

        urls.extend(found_urls)
    except Exception as e:
        print(f'Error: {str(e)}')

    return urls[0]

# Check if an HTML response is successful
def is_successful_http_response(url):
    try:
        response = requests.head(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return f'Error: {str(e)}'

# Check if URL is a local path
def is_local_path(path):
    parsed_url = urlparse(path)
    return parsed_url.scheme == '' or parsed_url.scheme in ('file', 'data')

# Convert a dictionary to JSON
def to_json(self, dictionary):
    return json.dumps(dictionary)

# Parse the HTML response for the Meeting ID, but uses web scraping on Zoom's 
# website. It can be useful if you want to confirm the PDF's meeting ID with 
# the one from the Zoom registration webpage.
# 
# import re
# 
# str_with_meeting_id = '{"number":81404263654,"encryptNumber":"}'
# match = re.search(r'"number":(\d+),', str_with_meeting_id)
# if match:
#     meeting_id = match.group(1)
#     print(meeting_id)
# else:
#     print("Meeting ID not found.")

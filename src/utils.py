from config_module import config
from datetime import datetime
import json
import pytz
import requests
import re
import os
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

def iso_time_to_readable(iso_string):
    # Parse ISO string to datetime dictionary in UTC
    utc_datetime = datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)

    # Convert to local time
    local_timezone = pytz.timezone(config['settings']['timezone'])
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
def extract_zoom_registration_links(text):
    urls = []

    try:
        url_pattern = re.compile(r'https?://alamedaca-gov\.zoom\.us/webinar/register/[a-zA-Z0-9_\-]+')
        found_urls = url_pattern.findall(text)

        urls.extend(found_urls)
    except Exception as e:
        print(f'Error: {str(e)}')

    return urls

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

# Get raw HTML from a local file path or URL
def get_html_content(path):
    if is_local_path(path):
        # Open HTML content from the locally saved path
        with open(path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        return html_content
    else:
        try:
            response = requests.get(path)
            response.raise_for_status()
            html_content = response.text

            return html_content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")

# Download the HTML to a local file to be used for development
def download_html_response(url_path, file_path):
    try:
        # Send an HTTP GET request to the provided URL
        response = requests.get(url_path)

        # Check if the request was successful
        if response.status_code == 200:
            # Create the 'data' folder if it doesn't exist
            if not os.path.exists('data'):
                os.makedirs('data')

            # Check if the file already exists
            if os.path.exists(file_path):
                # If the file exists, ask the user for action
                user_input = input(f"The file '{file_path}' already exists. Do you want to overwrite it? (y/n): ").lower()
                if user_input != 'y':
                    print("Operation aborted. Reusing existing file.")
                    return

            # Write the HTML content to a file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            
            print(f"HTML content saved to '{file_path}'")
        else:
            response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

# Create a hash table to count the number of occurrences of the first key
def are_all_strings_same(my_list):
    first_item = my_list[0]
    my_dict = {}

    for item in my_list:
        if not item in my_dict:
            my_dict[item] = 1
        else:
            my_dict[item] = my_dict[item] + 1
    
    if my_dict[first_item] == len(my_list):
        return True
    else:
        return False

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

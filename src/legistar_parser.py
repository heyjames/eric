from bs4 import BeautifulSoup
from config_module import config
import os
import re
import requests
import utils

class LegistarParser:
    """
    Read the HTML content from the Legistar website and parse the meeting data.
    """
    def __init__(self, path):
        self.path = path

    # Download the HTML to a local file to be used for development
    def download_html_response(self, url):
        try:
            file_path = config['settings']['debug_legistar_path']

            # Send an HTTP GET request to the provided URL
            response = requests.get(url)

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

    def get_data(self):
        if utils.is_local_path(self.path):
            if config['settings'].getboolean('debug_download_html'):
                html_content = self.download_html_response(config['settings']['legistar_url'])
            
            # Open HTML content from the locally saved path
            with open(self.path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        else:
            try:
                response = requests.get(self.path)
                response.raise_for_status()
                html_content = response.text
            except requests.exceptions.RequestException as e:
                print(f"Error fetching URL: {e}")

        # Initialize Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Upcoming Meetings selector
        bs_upcoming_meetings = soup.select('table[id="ctl00_ContentPlaceHolder1_gridUpcomingMeetings_ctl00"] tbody tr[id^="ctl00_ContentPlaceHolder1_gridUpcomingMeetings_ctl00__"]')

        # All Meetings selector
        bs_all_meetings = soup.select('table[id="ctl00_ContentPlaceHolder1_gridCalendar_ctl00"] tbody tr[id^="ctl00_ContentPlaceHolder1_gridCalendar_ctl00__"]')
        
        # Get a list of all the rows from each section
        upcoming_meetings = self.format_rows(bs_upcoming_meetings)
        all_meetings = self.format_rows(bs_all_meetings)

        return upcoming_meetings, all_meetings
    
    # Create a list of dictionaries by parsing the data (column) from each row
    def format_rows(self, rows):
        meetings = []

        for row in rows:
            id = self.parse_id(row)
            columns = row.select('td')

            name = self.parse_name(columns)
            date = self.parse_date(columns)
            time = self.parse_time(columns)
            location = self.parse_location(columns)
            details = self.parse_details(columns)
            agenda = self.parse_agenda(columns)
            video = self.parse_video(columns)

            is_meeting_canceled = self.parse_cancelled_meeting(location)

            meetings.append({
                'id': id,
                'name': name,
                'date': date,
                'time': time,
                'location': location,
                'details': details,
                'agenda': agenda,
                'video': video,
                'is_meeting_canceled': is_meeting_canceled
            })

        return meetings
    
    def parse_name(self, columns):
        name = columns[0].select_one("a[id$='_hypBody']").get_text(strip=True)
        return name
    
    def parse_date(self, columns):
        date = columns[1].get_text(strip=True)
        return date
    
    def parse_time(self, columns):
        time = columns[3].select_one("span[id$='_lblTime']").get_text(strip=True)
        return time
    
    def parse_location(self, columns):
        location = columns[4]
        for br_tag in location.find_all('br'):
            br_tag.replace_with('\n')
        location = location.get_text()
        return location
    
    def parse_details(self, columns):
        details = columns[5].select_one("a[id$='_hypMeetingDetail']")
        if details and details.has_attr('href'):
            details = config['settings']['legistar_url'] + details['href']
        else:
            details = ''
        return details
    
    def parse_agenda(self, columns):
        agenda = columns[6].select_one("a[id$='_hypAgenda']")
        if agenda and agenda.has_attr('href'):
            agenda = config['settings']['legistar_url'] + agenda['href']
        else:
            agenda = ''
        return agenda
    
    def parse_video(self, columns):
        video = columns[8].select_one("a[id$='_hypVideo']")
        if video and video.has_attr('onclick'):
            pattern = r"window\.open\('([^']+)',"
            match = re.search(pattern, video['onclick'])
            if match:
                video = config['settings']['legistar_url'] + match.group(1)
        else:
            video = ''
        return video
    
    def parse_id(self, row):
        if row.has_attr('id'):
            return int(row['id'][-1])
        else:
            return None

    def parse_cancelled_meeting(self, location):
        return 'cancel' in location.lower()
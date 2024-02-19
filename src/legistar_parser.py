import api
from bs4 import BeautifulSoup
from config import config
import re
import time
import utils

class LegistarParser:
    """
    Read the HTML content from the Legistar website and parse the meeting data.
    """
    def __init__(self):
        self.path = None
        self.formatted_meetings = None
        self.first_meeting_data = None
        self.first_non_canceled_meeting = None
        self.pdf_data = None
    
    # Format meeting data into dictionaries from Legistar website
    def set_formatted_meetings(self):
        # Get raw HTML
        html_content = utils.get_html_content(self.path)

        # Initialize Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Upcoming Meetings selector
        bs_upcoming_meetings = soup.select('table[id="ctl00_ContentPlaceHolder1_gridUpcomingMeetings_ctl00"] tbody tr[id^="ctl00_ContentPlaceHolder1_gridUpcomingMeetings_ctl00__"]')

        # All Meetings selector
        bs_all_meetings = soup.select('table[id="ctl00_ContentPlaceHolder1_gridCalendar_ctl00"] tbody tr[id^="ctl00_ContentPlaceHolder1_gridCalendar_ctl00__"]')
        
        # Get a list of all the rows from each section
        upcoming_meetings = self.format_rows(bs_upcoming_meetings)
        all_meetings = self.format_rows(bs_all_meetings)

        self.formatted_meetings = upcoming_meetings, all_meetings
    
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
    
    # Parse the Legistar website and create an dictionary of each meeting
    def set_path(self):
        if config['settings'].getboolean('debug'):
            self.path = config['settings']['debug_legistar_path']
        else:
            self.path = config['settings']['legistar_url']

    # Set the first non-canceled meeting (only supports Upcoming Meetings)
    def set_first_non_canceled_meeting(self):
        for meeting in self.formatted_meetings[0]:
            if meeting['is_meeting_canceled'] == False:
                self.first_non_canceled_meeting = meeting
                return
            
            time.sleep(1)

    # Set the Zoom data from the PDF
    def set_pdf_data(self):
        self.pdf_data = api.get_pdf_data(self.first_non_canceled_meeting)
    
    def set_first_meeting_data(self):
        self.first_meeting_data = utils.append_two_objects(self.first_non_canceled_meeting, self.pdf_data)
    
    def get_first_meeting_data(self):
        return self.first_meeting_data
    
    def run(self):
        self.set_path()
        self.set_formatted_meetings()
        self.set_first_non_canceled_meeting()
        self.set_pdf_data()
        self.set_first_meeting_data()
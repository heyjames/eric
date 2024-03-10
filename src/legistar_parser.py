from bs4 import BeautifulSoup
from config import config
from log import logger
import re
import time
import utils
import validate

class LegistarParser:
    """
    Read the HTML content from the Legistar website and parse the meeting data.
    """
    def __init__(self):
        self.path = None
        self.formatted_meetings = None
        self.first_non_canceled_meeting = None

        logger.info('Initializing LegistarParser instance')
    
    # Format meeting data into dictionaries from Legistar website
    def set_formatted_meetings(self):
        logger.debug('Starting LegistarParser set_formatted_meetings')
        
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

            is_meeting_canceled = self.parse_canceled_meeting(location)

            meetings.append({
                'id': id,
                'name': name,
                'date': date,
                'time': time,
                'location': location,
                'details': details,
                'agenda': agenda,
                'video': video,
                'is_meeting_canceled': is_meeting_canceled,
                'timestamp': None
            })

        return meetings
    
    def parse_name(self, columns):
        try:
            name = columns[0].select_one("a[id$='_hypBody']").get_text(strip=True)
            validate.is_not_blank(name)
            return name
        except Exception as e:
            raise ValueError('parse_name(): ' + str(e))
    
    def parse_date(self, columns):
        try:
            date = columns[1].get_text(strip=True)
            validate.is_date(date)
            return date
        except Exception as e:
            raise ValueError('parse_date(): ' + str(e))
    
    def parse_time(self, columns):
        try:
            time = columns[3].select_one("span[id$='_lblTime']").get_text(strip=True)
            validate.is_time(time)
            return time
        except Exception as e:
            raise ValueError('parse_time(): ' + str(e))
    
    def parse_location(self, columns):
        try:
            location = columns[4]
            for br_tag in location.find_all('br'):
                br_tag.replace_with('\n')
            location = location.get_text()
            validate.is_not_blank(location)
            return location
        except Exception as e:
            raise ValueError('parse_location(): ' + str(e))
    
    def parse_details(self, columns):
        try:
            details = columns[5].select_one("a[id$='_hypMeetingDetail']")
            if details and details.has_attr('href'):
                details = config['developer']['legistar_url'] + details['href']
            else:
                details = ''
            validate.is_string(details)
            return details
        except Exception as e:
            raise ValueError('parse_details(): ' + str(e))
    
    def parse_agenda(self, columns):
        try:
            agenda = columns[6].select_one("a[id$='_hypAgenda']")
            if agenda and agenda.has_attr('href'):
                agenda = config['developer']['legistar_url'] + agenda['href']
            else:
                agenda = ''
            validate.is_string(agenda)
            return agenda
        except Exception as e:
            raise ValueError('parse_agenda(): ' + str(e))
    
    def parse_video(self, columns):
        try:
            video = columns[8].select_one("a[id$='_hypVideo']")
            if video and video.has_attr('onclick'):
                pattern = r"window\.open\('([^']+)',"
                match = re.search(pattern, video['onclick'])
                if match:
                    video = config['developer']['legistar_url'] + match.group(1)
            else:
                video = ''
            validate.is_string(video)
            return video
        except Exception as e:
            raise ValueError('parse_video(): ' + str(e))

    def parse_id(self, row):
        try:
            id = int(row['id'][-1])
            validate.is_int(id)
            return id
        except Exception as e:
            return None

    def parse_canceled_meeting(self, location):
        try:
            result = 'cancel' in location.lower()
            validate.is_boolean(result)
            return result
        except Exception as e:
            raise ValueError('parse_canceled_meeting(): ' + str(e))
    
    # Parse the Legistar website and create an dictionary of each meeting
    def set_path(self):
        if config['developer'].getboolean('debug_enable'):
            self.path = config['developer']['debug_legistar_path']
        else:
            self.path = config['developer']['legistar_url']

    # Search the parsed meetings list until the first non-canceled meeting is 
    # found. Then set it as the first non-canceled meeting (only supports 
    # Upcoming Meetings)
    def set_first_non_canceled_meeting(self):
        logger.debug('Starting LegistarParser set_first_non_canceled_meeting')

        try:
            # Loop through Upcoming meetings section
            for meeting in self.formatted_meetings[0]:
                if meeting['is_meeting_canceled'] == False:
                    meeting['legistar_success'] = True
                    meeting['timestamp'] = utils.get_unix_time()

                    self.first_non_canceled_meeting = meeting
                    return
                
                time.sleep(1)
        except Exception as e:
            raise ValueError('set_first_non_canceled_meeting(): ' + str(e))

    def get_first_non_canceled_meeting(self):
        logger.debug('Starting LegistarParser get_first_non_canceled_meeting')

        return self.first_non_canceled_meeting
    
    def run(self):
        self.set_path()
        self.set_formatted_meetings()
        self.set_first_non_canceled_meeting()
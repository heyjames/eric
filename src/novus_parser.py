from bs4 import BeautifulSoup
from config import config
from log import logger
import re
import utils
import validate

class NovusParser:
    """
    Read the HTML content from the NovusAgenda website and parse the meeting data.
    """
    def __init__(self):
        self.path = None
        self.formatted_meetings = None
        self.is_regular_meeting = None
        self.first_meeting_agenda_raw_html = None
        self.meeting_agenda_zoom_urls = None
        self.are_zoom_links_same = None
        self.is_valid_zoom_registration_link = None
        self.first_meeting = None

        logger.info('Initializing NovusParser instance')

    # Parse raw HTML from the Novus calendar into a list of meetings 
    # dictionaries
    def set_formatted_meetings(self):
        logger.debug('Starting NovusParser set_formatted_meetings')

        # Get raw HTML
        html_content = utils.get_html_content(self.path)

        # Initialize Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Select the meetings table with Beautiful Soup
        novus_meetings = soup.select('table[id="ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridMeetings_ctl00"] tbody tr[id^="ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridMeetings_ctl00__"]')
        
        # Get a list of all the rows formatted
        self.formatted_meetings = self.format_rows(novus_meetings)
    
    # Create a list of dictionaries by parsing the data (column) from each row
    def format_rows(self, rows):
        meetings = []

        for row in rows:
            try:
                columns = row.select('td')

                id = self.parse_id(row)
                validate.is_int(id)

                date = self.parse_text(columns, 0)
                validate.is_date_novus(date)

                name = self.parse_text(columns, 1)
                validate.is_not_blank(name)

                location = self.parse_text(columns, 2)
                validate.is_not_blank(location)
                
                agenda_url = self.parse_agenda(columns)
                validate.is_string(agenda_url)

                meetings.append({
                    'id': id,
                    'date': date,
                    'name': name,
                    'location': location,
                    'agenda': agenda_url,
                })
            except Exception as e:
                raise ValueError('format_rows(): ' + str(e))

        return meetings
    
    def parse_text(self, columns, column):
        try:
            text = columns[column].get_text(strip=True)
            return text
        except Exception as e:
            raise ValueError('parse_text(): ' + str(e))
    
    # The link to the web-based agenda on the main Novus page is a JavaScript 
    # function that opens a new window when clicked, so this needs to be 
    # extracted and appended to the main URL
    def parse_agenda(self, columns):
        try:
            # Get the HTML element for the link
            a_el = columns[3].select_one('a')

            # Extract the partial URL
            pattern = r"window\.open\('([^']+)'"
            match = re.search(pattern, a_el['onclick'])

            if match:
                extracted_string = match.group(1)
                return config['developer']['novus_url'] + extracted_string
            else:
                print("Pattern not found.")
        except Exception as e:
            raise ValueError('parse_agenda(): ' + str(e))
    
    def parse_id(self, row):
        try:
            if row.has_attr('id'):
                return int(row['id'][-1])
            else:
                return None
        except Exception as e:
            return None
    
    # Check if it's a regular or special meeting
    def set_is_regular_meeting(self):
        logger.debug('Starting NovusParser set_is_regular_meeting')

        try:
            if 'Council Chambers' in self.first_meeting_agenda_raw_html:
                self.is_regular_meeting = True
            else:
                self.is_regular_meeting = False
        except Exception as e:
            raise ValueError('set_is_regular_meeting(): ' + str(e))
    
    def set_agenda_zoom_registration_links(self):
        logger.debug('Starting NovusParser set_agenda_zoom_registration_links')

        try:
            # Get the raw HTML from the first meeting's agenda's path
            self.first_meeting_agenda_raw_html = utils.get_html_content(self.agenda_path)

            # Extract all the Zoom registration URLs
            meeting_agenda_zoom_urls = utils.extract_zoom_registration_links(self.first_meeting_agenda_raw_html)

            if len(meeting_agenda_zoom_urls) > 0:
                self.meeting_agenda_zoom_urls = meeting_agenda_zoom_urls
        except Exception as e:
            raise ValueError('set_agenda_zoom_registration_links(): ' + str(e))

    def set_is_valid_zoom_registration_link(self):
        logger.debug('Starting NovusParser set_is_valid_zoom_registration_link')

        try:
            if len(self.meeting_agenda_zoom_urls) > 0:
                if len(self.meeting_agenda_zoom_urls) == 1:
                    # Avoid sending a request to the URL if debug mode is enabled
                    if config['developer'].getboolean('debug_enable'):
                        self.is_valid_zoom_registration_link = False
                    else:
                        self.is_valid_zoom_registration_link = utils.is_valid_zoom_registration_link(self.meeting_agenda_zoom_urls[0])

                if len(self.meeting_agenda_zoom_urls) > 1:
                    # Check if all 4 extracted Zoom links are the same
                    self.are_zoom_links_same = utils.are_all_strings_same(self.meeting_agenda_zoom_urls)

                    # Return the first Novus meeting data dictionary if all 4 Zoom registration 
                    # links are the same
                    if self.are_zoom_links_same:
                        # Avoid sending a request to the URL if debug mode is enabled
                        if config['developer'].getboolean('debug_enable'):
                            self.is_valid_zoom_registration_link = False
                        else:
                            self.is_valid_zoom_registration_link = utils.is_valid_zoom_registration_link(self.meeting_agenda_zoom_urls[0])
        except Exception as e:
            raise ValueError('set_is_valid_zoom_registration_link(): ' + str(e))

    def set_first_meeting(self):
        logger.debug('Starting NovusParser set_first_meeting')

        try:
            unix_time = utils.get_unix_time()

            if self.is_regular_meeting == False:
                self.first_meeting = {
                    'novus_success': False,
                    'novus_error': 'The first NovusAgenda meeting is not a regular meeting.',
                    'novus_timestamp': unix_time
                }
            else:
                if self.are_zoom_links_same:
                    self.first_meeting = {
                        'novus_success': True,
                        'novus_timestamp': unix_time,
                        'novus_zoom_registration_link': self.meeting_agenda_zoom_urls[0],
                        'novus_is_valid_zoom_registration_link': self.is_valid_zoom_registration_link
                    }
                else:
                    self.first_meeting = {
                        'novus_success': False,
                        'novus_error': 'Zoom links are not the same',
                        'novus_timestamp': unix_time
                    }
        except Exception as e:
            raise ValueError('set_first_meeting(): ' + str(e))
    
    # Use a file path or URL if debug mode is enabled
    def set_path(self):
        logger.debug('Starting NovusParser set_path')

        if config['developer'].getboolean('debug_enable'):
            self.path = config['developer']['debug_novus_path']
        else:
            self.path = config['developer']['novus_url']
    
    # Unlike Legistar, we can view a meeting's agenda in HTML, so we get the 
    # first meeting's agenda's URL, or file path if debug mode is enabled
    def set_agenda_path(self):
        logger.debug('Starting NovusParser set_agenda_path')

        if config['developer'].getboolean('debug_enable'):
            self.agenda_path = config['developer']['debug_novus_agenda_path']
        else:
            self.agenda_path = self.formatted_meetings[0]['agenda']
    
    def get_first_meeting(self):
        return self.first_meeting

    def run(self):
        self.set_path()
        self.set_formatted_meetings()
        self.set_agenda_path()
        self.set_agenda_zoom_registration_links()
        self.set_is_valid_zoom_registration_link()
        self.set_is_regular_meeting()
        self.set_first_meeting()
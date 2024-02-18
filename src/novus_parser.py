from bs4 import BeautifulSoup
from config_module import config
import re
import utils

class NovusParser:
    """
    Read the HTML content from the NovusAgenda website and parse the meeting data.
    """
    def __init__(self, path):
        self.path = path

    def get_formatted_novus_meetings(self):
        # Get raw HTML
        html_content = utils.get_html_content(self.path)

        # Initialize Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Select the meetings table with Beautiful Soup
        novus_meetings = soup.select('table[id="ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridMeetings_ctl00"] tbody tr[id^="ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridMeetings_ctl00__"]')
        
        # Get a list of all the rows formatted
        formatted_novus_meetings = self.format_rows(novus_meetings)

        return formatted_novus_meetings
    
    # Create a list of dictionaries by parsing the data (column) from each row
    def format_rows(self, rows):
        meetings = []

        for row in rows:
            id = self.parse_id(row)
            columns = row.select('td')

            date = self.parse_text(columns)
            name = self.parse_text(columns)
            location = self.parse_text(columns)
            agenda_url = self.parse_agenda(columns)

            meetings.append({
                'id': id,
                'date': date,
                'name': name,
                'location': location,
                'agenda': agenda_url,
            })

        return meetings
    
    def parse_text(self, columns):
        text = columns[0].get_text(strip=True)
        return text
    
    def parse_agenda(self, columns):
        a_el = columns[3].select_one('a')

        pattern = r"window\.open\('([^']+)'"
        match = re.search(pattern, a_el['onclick'])

        if match:
            extracted_string = match.group(1)
            return 'https://alameda.novusagenda.com/agendapublic/' + extracted_string
        else:
            print("Pattern not found.")
    
    def parse_id(self, row):
        if row.has_attr('id'):
            return int(row['id'][-1])
        else:
            return None
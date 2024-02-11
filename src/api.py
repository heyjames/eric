from config_module import config
from legistar_parser import LegistarParser
from pdf_parser import PDFParser
import time

# Parse the Legistar website and create an dictionary of each meeting
def get_formatted_upcoming_and_all_meetings():
    legistar_path = config['settings']['LEGISTAR_URL']
    # legistar_path = 'data/legistar_html_content.html'

    legistar_website = LegistarParser(legistar_path)

    upcoming_meetings, all_meetings = legistar_website.get_data()

    return upcoming_meetings, all_meetings

# Parse the PDF for the Zoom registration link and check its HTTP response
def get_pdf_data(path):
    pdf_parser = PDFParser(path)
    pdf_data = pdf_parser.get_data()

    return pdf_data

# Combine the PDF and meeting data
def combine_pdf_and_meeting_data(meeting_data, pdf_data):
    result = {}
    result.update(meeting_data)
    result.update(pdf_data)

    return result

# Get the first non-canceled meeting
def get_first_non_canceled_meeting(meetings):
    for meeting in meetings:
        if meeting['is_meeting_canceled'] == False:
            return meeting
        
        time.sleep(1)

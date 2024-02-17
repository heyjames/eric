from config_module import config
from legistar_parser import LegistarParser
from pdf_parser import PDFParser
from gmail import send_message
import time

def send_emails(meeting_data):
    if not config['email_broken_zoom_link']['recipients']:
        return
    
    email_content = {
        'to': config['email_broken_zoom_link']['recipients'],
        'subject': 'Broken Zoom Link Detected',
        'body': 'Broken Zoom link detected for meeting:\n' \
            + meeting_data['name'] \
            + ', ' + meeting_data['date'] \
            + ', ' + meeting_data['time']
    }

    send_message(email_content)

# Parse the Legistar website and create an dictionary of each meeting
def get_formatted_upcoming_and_all_meetings():
    if config['settings'].getboolean('debug'):
        legistar_path = config['settings']['debug_legistar_path']
    else:
        legistar_path = config['settings']['legistar_url']

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

# Get the first non-canceled meeting (only supports Upcoming Meetings)
def get_first_non_canceled_meeting(meetings):
    for meeting in meetings:
        if meeting['is_meeting_canceled'] == False:
            return meeting
        
        time.sleep(1)

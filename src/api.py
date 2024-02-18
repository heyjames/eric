from config_module import config
from legistar_parser import LegistarParser
from novus_parser import NovusParser
from pdf_parser import PDFParser
from gmail import send_message
import utils
import time

def get_first_novus_meeting_data():
    novus_parser = NovusParser(config['settings']['debug_novus_path']) # local path
    novus_meetings = novus_parser.get_formatted_novus_meetings() # parse raw HTML into a meetings dictionary
    first_novus_meeting_agenda_url = novus_meetings[0]['agenda'] # get the agenda url from the first meeting. Not used in debug mode.
    first_novus_meeting_agenda_raw_html = utils.get_html_content(config['settings']['debug_novus_agenda_path']) # get the raw HTML from the agenda url
    novus_meeting_agenda_zoom_urls = utils.extract_zoom_registration_links(first_novus_meeting_agenda_raw_html) # extract all the Zoom registration urls
    same_zoom_url_count = utils.count_same_strings_from_list(novus_meeting_agenda_zoom_urls)
    if same_zoom_url_count == 4:
        # Use False for testing purposes
        if config['settings'].getboolean('debug'):
            is_valid_zoom_registration_link = False
        else:
            is_valid_zoom_registration_link = utils.is_successful_http_response(novus_meeting_agenda_zoom_urls[0])

        my_dict = {
            'novus_success': True,
            'novus_timestamp': utils.get_unix_time(),
            'novus_zoom_registration_link': novus_meeting_agenda_zoom_urls[0],
            'novus_is_valid_zoom_registration_link': is_valid_zoom_registration_link
        }
    else:
        my_dict = {
            'novus_success': False,
            'novus_timestamp': utils.get_unix_time()
        }

    return my_dict

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

def get_first_meeting_data():
    # Format meeting data into dictionaries from Legistar website
    upcoming_meetings, all_meetings = get_formatted_upcoming_and_all_meetings()

    # Get the first non-canceled meeting
    first_non_canceled_meeting =  get_first_non_canceled_meeting(upcoming_meetings)

    # Get the Zoom registration link from the PDF and check its HTTP response
    if config['settings'].getboolean('debug'):
        # pdf_path = config['settings']['debug_pdf_url']
        pdf_path = config['settings']['debug_pdf_path']
        pdf_data = get_pdf_data(pdf_path)
    else:
        pdf_data = get_pdf_data(first_non_canceled_meeting['agenda'])

    # Combine the meeting data with the PDF data into one dictionary
    result = combine_pdf_and_meeting_data(first_non_canceled_meeting, pdf_data)

    return result
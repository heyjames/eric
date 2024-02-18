from config_module import config
from legistar_parser import LegistarParser
from novus_parser import NovusParser
from pdf_parser import PDFParser
import gmail
import utils
import time

def get_first_novus_meeting_data():
    # Use a file path or URL if debug mode is enabled
    if config['settings'].getboolean('debug'):
        path = config['settings']['debug_novus_path']
    else:
        path = config['settings']['novus_url']
    
    # Initialize class
    novus_parser = NovusParser(path)

    # Parse raw HTML from the Novus calendar into a list of meetings 
    # dictionaries
    novus_meetings = novus_parser.get_formatted_novus_meetings()

    # Unlike Legistar, we can view a meeting's agenda in HTML, so we get the 
    # first meeting's agenda's URL, or file path if debug mode is enabled
    if config['settings'].getboolean('debug'):
        agenda_path = config['settings']['debug_novus_agenda_path']
    else:
        agenda_path = novus_meetings[0]['agenda']

    # Get the raw HTML from the first meeting's agenda's path
    first_novus_meeting_agenda_raw_html = utils.get_html_content(agenda_path)

    # Detect if it's a regular or special meeting
    if not novus_parser.is_novus_regular_meeting(first_novus_meeting_agenda_raw_html):
        print('The first NovusAgenda meeting is not a regular meeting. Return None.')
        return None

    # Extract all the Zoom registration URLs
    novus_meeting_agenda_zoom_urls = utils.extract_zoom_registration_links(first_novus_meeting_agenda_raw_html)

    # Because there are two of the same Zoom registration links in their 
    # meeting agenda (for some reason, it's repeated in the closed session), 
    # it actually gets 4 because of the HTML href attribute
    same_zoom_url_count = utils.count_same_strings_from_list(novus_meeting_agenda_zoom_urls)

    # Return the first Novus meeting data dictionary if all 4 Zoom registration 
    # links are the same
    if same_zoom_url_count == 4:
        # Avoid sending a request to the URL if debug mode is enabled
        if config['settings'].getboolean('debug'):
            is_valid_zoom_registration_link = False
        else:
            is_valid_zoom_registration_link = utils.is_successful_http_response(novus_meeting_agenda_zoom_urls[0])

        first_novus_meeting_data = {
            'novus_success': True,
            'novus_timestamp': utils.get_unix_time(),
            'novus_zoom_registration_link': novus_meeting_agenda_zoom_urls[0],
            'novus_is_valid_zoom_registration_link': is_valid_zoom_registration_link
        }
    else:
        first_novus_meeting_data = {
            'novus_success': False,
            'novus_timestamp': utils.get_unix_time()
        }

    return first_novus_meeting_data

def send_emails(meeting_data):
    # Return if no recipients are listed in the config file
    if not config['email_broken_zoom_link']['recipients']:
        print('No email recipients listed in config.cfg')
        return
    
    # Return if Zoom registration link is valid
    if meeting_data['is_valid_zoom_registration_link']:
        return
    
    email_content = {
        'to': config['email_broken_zoom_link']['recipients'],
        'subject': 'Broken Zoom Link Detected',
        'body': 'Broken Zoom link detected for meeting:\n' \
            + meeting_data['name'] \
            + ', ' + meeting_data['date'] \
            + ', ' + meeting_data['time']
    }

    gmail.send_message(email_content)

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
def get_pdf_data(first_non_canceled_meeting):
    # Use a file path or URL if debug mode is enabled
    if config['settings'].getboolean('debug'):
        path = config['settings']['debug_pdf_path']
    else:
        path = first_non_canceled_meeting['agenda']
    
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
    
    # Get the Zoom data from the PDF
    pdf_data = get_pdf_data(first_non_canceled_meeting)

    # Combine the meeting data with the PDF data into one dictionary
    result = combine_pdf_and_meeting_data(first_non_canceled_meeting, pdf_data)

    return result
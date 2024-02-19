from config_module import config
from legistar_parser import LegistarParser
from novus_parser import NovusParser
from pdf_parser import PDFParser
import gmail

def get_first_novus_meeting_data():
    try:
        novus_parser = NovusParser()
        novus_parser.run()
        return novus_parser.get_first_meeting_data()

    except Exception as e:
        print(f'Error: {e}')

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

def get_first_meeting_data():
    # Format meeting data into dictionaries from Legistar website
    upcoming_meetings, all_meetings = get_formatted_upcoming_and_all_meetings()

    # Get the first non-canceled meeting
    first_non_canceled_meeting =  LegistarParser.get_first_non_canceled_meeting(upcoming_meetings)
    
    # Get the Zoom data from the PDF
    pdf_data = get_pdf_data(first_non_canceled_meeting)

    # Combine the meeting data with the PDF data into one dictionary
    result = combine_pdf_and_meeting_data(first_non_canceled_meeting, pdf_data)

    return result
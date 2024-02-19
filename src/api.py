from config import config
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

def get_first_legistar_meeting_data():
    try:
        legistar_parser = LegistarParser()
        legistar_parser.run()
        return legistar_parser.get_first_meeting_data()

    except Exception as e:
        print(f'Error: {e}')

def send_emails(meeting_data):
    try:
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

    except Exception as e:
        print(f'Error: {e}')

# Parse the PDF for the Zoom registration link and check its HTTP response
def get_pdf_data(first_non_canceled_meeting):
    try:
        # Use a file path or URL if debug mode is enabled
        if config['settings'].getboolean('debug'):
            path = config['settings']['debug_pdf_path']
        else:
            path = first_non_canceled_meeting['agenda']
        
        pdf_parser = PDFParser(path)
        pdf_data = pdf_parser.get_data()

        return pdf_data
    except Exception as e:
        print(f'Error: {e}')
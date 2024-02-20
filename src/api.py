from config import config
import gmail
from legistar_parser import LegistarParser
from novus_parser import NovusParser
from pdf_parser import PDFParser
import utils

def get_first_novus_meeting():
    try:
        novus_parser = NovusParser()
        novus_parser.run()
        return novus_parser.get_first_meeting()

    except Exception as e:
        print(f'Error: {e}')

def get_first_legistar_meeting():
    try:
        legistar_parser = LegistarParser()
        legistar_parser.run()

        first_non_canceled_meeting = legistar_parser.get_first_non_canceled_meeting()
        pdf_data = get_pdf(first_non_canceled_meeting)
        
        # Combine the meeting and pdf data
        return utils.append_dictionaries([first_non_canceled_meeting, pdf_data])

    except Exception as e:
        # print(f'Error: {traceback.format_exc()}')
        print(f'Error: {e}')

# Parse the PDF for the Zoom registration link and check its HTTP response
def get_pdf(meeting):
    try:
        pdf_parser = PDFParser(meeting)
        pdf_parser.run()
        return pdf_parser.get_data()
    
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
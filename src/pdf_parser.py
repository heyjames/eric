from config import config
import fitz # PyMuPDF
import requests
import utils

class PDFParser:
    """
    Read the PDF text, extract zoom registration link from text, and check 
    the link for a successful response.
    """
    def __init__(self, first_non_canceled_meeting):
        self.first_non_canceled_meeting = first_non_canceled_meeting
        self.path = None
        self.pdf_text = None
        self.zoom_registration_link = None
        self.is_valid_zoom_registration_link = None
        self.data = None
    
    def set_path(self):
        # Use a file path or URL if debug mode is enabled
        if config['settings'].getboolean('debug'):
            self.path = config['settings']['debug_pdf_path']
        else:
            self.path = self.first_non_canceled_meeting['agenda']

    # Handle local or remote URL, and then parse the PDF and return the text 
    # using the PyMuPDF module
    def set_pdf_text(self):
        try:
            # Handle local or remote URL
            if utils.is_local_path(self.path):
                pdf_document = fitz.open(self.path)
            else:
                response = requests.get(self.path)
                response.raise_for_status() # Raise an exception for bad responses

                pdf_document = fitz.open(stream=response.content, filetype='pdf')

            # The Zoom registration link is always on the first page of the 
            # agenda
            first_page = pdf_document[0]

            self.pdf_text = first_page.get_text()

            pdf_document.close()
        except requests.exceptions.RequestException as e:
            raise ValueError(f'Request failed: {str(e)}')
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")

    def set_zoom_registration_link(self):
        # Extract the first Zoom registration link from the PDF text
        self.zoom_registration_link = utils.extract_zoom_registration_links(self.pdf_text)[0]

    def set_is_valid_zoom_registration_link(self):
        # If a Zoom registration link exists, check for a successful response
        if self.zoom_registration_link:
            # Use False for testing purposes
            if config['settings'].getboolean('debug'):
                self.is_valid_zoom_registration_link = False
            else:
                self.is_valid_zoom_registration_link = utils.is_successful_http_response(self.zoom_registration_link)
    
    def set_data(self):
        self.data = {
            'pdf_success': True,
            'pdf_timestamp': utils.get_unix_time(),
            'pdf_zoom_registration_link': self.zoom_registration_link,
            'pdf_is_valid_zoom_registration_link': self.is_valid_zoom_registration_link
        }
    
    def get_data(self):
        return self.data
    
    def run(self):
        self.set_path()
        self.set_pdf_text()
        self.set_zoom_registration_link()
        self.set_is_valid_zoom_registration_link()
        self.set_data()
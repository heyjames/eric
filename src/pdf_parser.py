from config import config
import fitz # PyMuPDF
from log import logger
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
        
        logger.info('Initializing PDFParser instance')
    
    def set_path(self):
        logger.debug('Starting PDFParser set_path')

        # Use a file path or URL if debug mode is enabled
        if config['developer'].getboolean('debug_enable'):
            self.path = config['developer']['debug_pdf_path']
        else:
            self.path = self.first_non_canceled_meeting['agenda']

    # Handle local or remote URL, and then parse the PDF and return the text 
    # using the PyMuPDF module
    def set_pdf_text(self):
        logger.debug('Starting PDFParser set_pdf_text')

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
        logger.debug('Starting PDFParser set_zoom_registration_link')

        # Extract the first Zoom registration link from the PDF text
        zoom_registration_links = utils.extract_zoom_registration_links(self.pdf_text)
        if len(zoom_registration_links) > 0:
            self.zoom_registration_link = zoom_registration_links[0]

    def set_is_valid_zoom_registration_link(self):
        logger.debug('Starting PDFParser set_is_valid_zoom_registration_link')

        # If a Zoom registration link exists, check for a successful response
        if self.zoom_registration_link:
            # Use False for testing purposes
            if config['developer'].getboolean('debug_enable'):
                self.is_valid_zoom_registration_link = False
            else:
                self.is_valid_zoom_registration_link = utils.is_valid_zoom_registration_link(self.zoom_registration_link)
    
    def set_data(self):
        logger.debug('Starting PDFParser set_data')

        # If no Zoom registration link was found
        if self.zoom_registration_link == None and self.is_valid_zoom_registration_link == None:
            self.data = {
                'pdf_success': False,
                'pdf_timestamp': utils.get_unix_time(),
                'pdf_zoom_registration_link': self.zoom_registration_link,
                'pdf_is_valid_zoom_registration_link': self.is_valid_zoom_registration_link
            }
        else:
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
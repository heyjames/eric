from config_module import config
import fitz # PyMuPDF
import requests
import utils

class PDFParser:
    """
    Read the PDF text, extract zoom registration link from text, and check 
    the link for a successful response.
    """
    def __init__(self, path):
        self.zoom_registration_link = None
        self.is_valid_zoom_registration_link = None
        self._initialize(path)

    def _initialize(self, path):
        # Read the PDF text from the local file or URL using the PyMuPDF 
        # module.
        pdf_text = self.read_pdf(path)

        # Extract the Zoom registration link from the PDF text
        zoom_registration_link = utils.extract_zoom_registration_link(pdf_text)

        # If a Zoom registration link exists, check for a successful response
        if zoom_registration_link:
            # Use False for testing purposes
            if config['settings'].getboolean('debug'):
                is_valid_zoom_registration_link = False
            else:
                is_valid_zoom_registration_link = utils.is_successful_http_response(zoom_registration_link)

        self.zoom_registration_link = zoom_registration_link
        self.is_valid_zoom_registration_link = is_valid_zoom_registration_link

    # Handle local or remote URL, and then parse the PDF using the PyMuPDF 
    # module and return the text
    def read_pdf(self, path):
        try:
            # Handle local or remote URL
            if utils.is_local_path(path):
                pdf_document = fitz.open(path)
            else:
                response = requests.get(path)
                response.raise_for_status() # Raise an exception for bad responses

                pdf_document = fitz.open(stream=response.content, filetype='pdf')

            # The Zoom registration link is always on the first page of the 
            # agenda
            first_page = pdf_document[0]

            pdf_text = first_page.get_text()

            pdf_document.close()

            return pdf_text
        except requests.exceptions.RequestException as e:
            raise ValueError(f'Request failed: {str(e)}')
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")
    
    def get_data(self):
        return {
            'time': utils.get_unix_time(),
            'zoom_registration_link': self.zoom_registration_link,
            'is_valid_zoom_registration_link': self.is_valid_zoom_registration_link
        }
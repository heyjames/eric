from config import config
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().handlers = []

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler('../log.log')
log_level = getattr(logging, config['developer']['log_level'])
file_handler.setLevel(log_level)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
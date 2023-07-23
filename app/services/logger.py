import logging

# Create a logger object
logger = logging.getLogger(__name__)

# Set the log level - this can be DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.setLevel(logging.DEBUG)

# Create file handler which logs messages
file_handler = logging.FileHandler('../../application.log')
file_handler.setLevel(logging.DEBUG)

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

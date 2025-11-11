import logging

# Create a custom logger
logger = logging.getLogger("pmbot")

# Create handlers
console_handler = logging.StreamHandler()

# Create formatters and add it to handlers
console_format = logging.Formatter('[%(name)s] %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)

# Add handlers to the logger
logger.addHandler(console_handler)

# Set log level
logger.setLevel(logging.DEBUG)
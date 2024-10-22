import os
import logging
import logging.handlers

def setup_logger(name, log_file, level=logging.INFO, max_bytes=10*1024*1024, backup_count=5):
    """File to set up a logger with a specific name and log file."""
    # create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create a rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setLevel(level)

    # create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # create a formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
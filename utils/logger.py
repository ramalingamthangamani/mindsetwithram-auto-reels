import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from config import LOG_FILE

def get_logger(name):
    """
    Returns a configured logger with rotating file handler and console output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # File handler (Rotating max 5 MB, keep 5 backups)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Stream handler (Console)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_formatter = logging.Formatter('%(levelname)s: %(message)s')
        stream_handler.setFormatter(stream_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        
    return logger

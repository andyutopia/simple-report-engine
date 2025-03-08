import logging
import os
from datetime import datetime

def setup_logger():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger('ReportGenerator')
    logger.setLevel(logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler(
        f"logs/report_{datetime.now().strftime('%Y%m%d')}.log"
    )
    console_handler = logging.StreamHandler()
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set formatters to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
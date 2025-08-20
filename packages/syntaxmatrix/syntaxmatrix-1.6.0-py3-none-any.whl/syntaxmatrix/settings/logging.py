import logging
import sys
from logging.handlers import RotatingFileHandler
from syntaxmatrix.project_root import detect_project_root


def configure_logging():
    """Set up robust error logging to file"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)  # Capture only errors and above
    
    # File handler with rotation (5MB per file, keep 3 backups)
    file_handler = RotatingFileHandler(
        filename=f'{detect_project_root()}/smx_logs.log',
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    
    # Error formatting with tracebacks
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    # Capture unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception

# Initialize logging when module loads
configure_logging()

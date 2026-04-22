import logging
import sys
from settings import settings

# Log format configuration
# Example: 2023-10-27 10:00:00,123 - INFO - [main.py:15] - Test message
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

def configure_logging():
    """Configure the application's global logging.

    If the configuration variable ``settings.LOG_FILE`` is set, messages will
    also be written to that plain text file in addition to standard output.
    """
    
    # Obtain log level from settings (e.g. "DEBUG", "INFO")
    numeric_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Basic configuration
    # Build a list of handlers starting with stdout
    handlers = [logging.StreamHandler(sys.stdout)]
    # If a log file path is specified, append a file handler
    if settings.LOG_FILE:
        try:
            fh = logging.FileHandler(settings.LOG_FILE)
            fh.setFormatter(logging.Formatter(LOG_FORMAT))
            handlers.append(fh)
        except Exception as err:  # pragma: no cover - best effort
            logging.getLogger("api").warning(
                "Could not open log file %s: %s", settings.LOG_FILE, err
            )

    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        handlers=handlers
    )
    
    # Adjust noisy logs from libraries
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING) # Reduce noise from normal HTTP requests

    # Create root logger for testing
    logger = logging.getLogger("api")
    logger.info(f"Logging configured. Level: {settings.LOG_LEVEL}")

# Quick logger instance to import if you need one fast,
# although it's recommended to use logging.getLogger(__name__) in each file.
def get_logger(name: str):
    return logging.getLogger(name)

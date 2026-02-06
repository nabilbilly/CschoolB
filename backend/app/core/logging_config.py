import logging
import sys
from app.core.config import settings

def setup_logging():
    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Force new configuration to override any existing (e.g., uvicorn defaults)
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )

    # Specific logger for application
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    
    # Silence uvicorn access logs to avoid double logging
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    return logger

setup_logging()

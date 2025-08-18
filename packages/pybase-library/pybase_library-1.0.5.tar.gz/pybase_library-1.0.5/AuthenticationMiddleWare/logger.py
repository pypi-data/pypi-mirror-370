import logging
import os

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

def setup_logging(level=LOG_LEVEL, format_str=LOG_FORMAT):
    """Setup logging configuration for AuthenticationMiddleWare"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True  # Override existing configuration
    )
    
    # Set specific logger levels
    auth_logger = logging.getLogger('AuthenticationMiddleWare')
    auth_logger.setLevel(getattr(logging, level.upper()))
    
    return auth_logger

import logging
import sys
import os

def configure_logging():
    # Set up logging to stdout
    root_logger = logging.getLogger()
    stdout_handler = logging.StreamHandler(sys.stdout)
    root_logger.addHandler(stdout_handler)

    # Set the log format and level
    log_format = '%(asctime)s %(thread)d [%(levelname)s] %(message)s'
    log_level = logging.DEBUG if os.environ.get('DEV_MODE', 'disabled') == 'enabled' else logging.INFO

    # Configure logging to append to Docker container logs
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[stdout_handler],
        force=True  # This ensures we override any existing configuration
    )
    
    # Ensure discord.py's logger doesn't overwhelm your logs
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)
import json
import logging
import logging.config

def setup_logging():
    """Set up logging according to the config file."""
    with open('dsstools/log/config.json', 'r') as config_file:
        config = json.load(config_file)
    logging.config.dictConfig(config)

setup_logging()

def get_logger(name: str):
    """Return logger name."""
    return logging.getLogger(name)

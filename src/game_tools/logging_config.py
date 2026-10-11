import logging
import sys
import time

from game_tools.util import fail

def configure_logging(path_to_log_file):
    if path_to_log_file:
        logging.Formatter.converter = time.gmtime

        try:
            logging.basicConfig(
                datefmt = '%Y-%m-%dT%H:%M:%SZ',
                encoding = 'utf-8',
                filemode = 'w',
                filename = path_to_log_file,
                format = '%(asctime)s - %(levelname)s - %(message)s',
                level = logging.DEBUG,
            )
        except OSError as e:
            fail('Logging config failed:', e)
    else:
        logging.getLogger().addHandler(logging.NullHandler())

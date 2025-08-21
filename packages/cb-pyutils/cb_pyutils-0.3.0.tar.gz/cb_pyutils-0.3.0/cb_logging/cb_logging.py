import os
import logging
from logging.handlers import RotatingFileHandler


class CBLogger():
    """
    A simple logger class for logging messages to console and file.
    """

    def __init__(self, do_file_logging=True, log_file_name='cb_logging.log'):
        self.do_file_logging = do_file_logging
        self.log_file_name = log_file_name

        self.setup_logger()
        self.setup_console_handler()
        if do_file_logging:
            self.setup_file_handler()

    def setup_logger(self):
        # Set up logging
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)

    def setup_console_handler(self):
        # Console handler for logging to stdout
        self.log_handler_console = logging.StreamHandler()
        self.log_handler_console.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self.log.addHandler(self.log_handler_console)

    def setup_file_handler(self):
        # File handler for logging to a file

        do_rollover = False
        if os.path.exists(self.log_file_name):
            do_rollover = True
        # Create a rotating file handler
        self.log_handler_file = RotatingFileHandler(
            self.log_file_name, maxBytes=10 * 1024 * 1024, backupCount=10)
        self.log_handler_file.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s"))
        # Rotate existing log file before starting if it exists
        if do_rollover:
            self.log_handler_file.doRollover()
        self.log.addHandler(self.log_handler_file)

    def info(self, message):
        self.log.info(message)

    def debug(self, message):
        self.log.debug(message)

    def error(self, message):
        self.log.error(message)

    def warning(self, message):
        self.log.warning(message)

    def critical(self, message):
        self.log.critical(message)

    def close(self):
        for handler in self.log.handlers[:]:
            handler.close()
            self.log.removeHandler(handler)

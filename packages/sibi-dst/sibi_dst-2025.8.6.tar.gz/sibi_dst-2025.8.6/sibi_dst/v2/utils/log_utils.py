import logging
import os
import sys
import time
from typing import Optional

class Logger:
    """
    Handles the creation, setup, and management of logging functionalities.
    """
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, log_dir: str, logger_name: str, log_file: str, debug: bool = False):
        """
        Initialize the Logger instance.
        :param log_dir: Directory where logs are stored.
        :param logger_name: Name of the logger instance.
        :param log_file: Base name of the log file.
        :param debug: Whether to enable debug mode (defaults to False).
        """
        self.log_dir = log_dir
        self.logger_name = logger_name
        self.log_file = log_file
        self.debug_mode = debug  # Add a debug flag
        self.logger = None
        self._setup()

    def _setup(self):
        """Set up the logger with file and console handlers."""
        # Ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Get the name of the calling script
        calling_script = os.path.splitext(os.path.basename(sys.argv[0]))[0]

        # Create a log file path
        log_file_path = os.path.join(self.log_dir, f"{self.log_file}_{calling_script}.log")

        # Delete the existing log file if it exists
        if os.path.exists(log_file_path):
            os.remove(log_file_path)

        # Create a logger
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(self._get_log_level())  # Dynamically set the log level

        # Create a formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        formatter.converter = time.localtime  # Set local time explicitly

        # Create a file handler
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Create a console handler (optional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _get_log_level(self) -> int:
        """
        Determine the logging level based on the debug flag.
        :return: Logging level (DEBUG if debug is True, otherwise INFO).
        """
        return logging.DEBUG if self.debug_mode else logging.INFO

    @classmethod
    def default_logger(
            cls,
            log_dir: str = './logs/',
            logger_name: Optional[str] = None,
            log_file: Optional[str] = None,
            debug: bool = False
    ) -> 'Logger':
        """
        Class-level method to create a default logger with generic parameters.
        :param log_dir: Directory where logs are stored (defaults to './logs/').
        :param logger_name: Name of the logger (defaults to __name__).
        :param log_file: Name of the log file (defaults to logger_name).
        :param debug: Whether to enable debug mode (defaults to False).
        :return: Instance of Logger.
        """
        logger_name = logger_name or __name__
        log_file = log_file or logger_name
        return cls(log_dir=log_dir, logger_name=logger_name, log_file=log_file, debug=debug)

    def set_level(self, level: int):
        """
        Set the logging level for the logger.
        :param level: Logging level (e.g., logging.DEBUG, logging.INFO).
        """
        self.logger.setLevel(level)

    def debug(self, msg: str):
        """Log a debug message."""
        self.logger.debug(msg)

    def info(self, msg: str):
        """Log an info message."""
        self.logger.info(msg)

    def warning(self, msg: str):
        """Log a warning message."""
        self.logger.warning(msg)

    def error(self, msg: str):
        """Log an error message."""
        self.logger.error(msg)

    def critical(self, msg: str):
        """Log a critical message."""
        self.logger.critical(msg)
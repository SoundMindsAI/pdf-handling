#!/usr/bin/env python3
"""
Logging Configuration Module

This module provides a centralized logging configuration for all scripts in the project.
It configures:
- Console output with colored formatting based on log level
- File output with detailed formatting including timestamps
- Customizable log levels for different environments
- Separate log files for each run with date-based naming

Usage:
    from logging_config import configure_logging, get_logger
    
    # Configure logging at the start of your script
    configure_logging()
    
    # Get a logger in each module
    logger = get_logger(__name__)
    
    # Use the logger
    logger.debug("Detailed debug information")
    logger.info("General information")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical error")
"""

import os
import sys
import logging
import datetime
from pathlib import Path


# ANSI color codes for colored console output
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"


# Custom formatter for console output with colors
class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Colors.BLUE + "%(levelname)s" + Colors.RESET + " - %(message)s",
        logging.INFO: Colors.GREEN + "%(levelname)s" + Colors.RESET + " - %(message)s",
        logging.WARNING: Colors.YELLOW + "%(levelname)s" + Colors.RESET + " - %(message)s",
        logging.ERROR: Colors.RED + "%(levelname)s" + Colors.RESET + " - %(message)s",
        logging.CRITICAL: Colors.BOLD + Colors.RED + "%(levelname)s" + Colors.RESET + " - %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def configure_logging(console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Configure logging for the application.
    
    Args:
        console_level: Logging level for console output (default: INFO)
        file_level: Logging level for file output (default: DEBUG)
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate a timestamp for the log filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"pdf_processing_{timestamp}.log")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all logs
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColoredFormatter())
    
    # Create file handler with detailed output
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(file_format)
    
    # Add handlers to the root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Log the start of logging
    root_logger.info(f"Logging configured - Log file: {log_file}")
    return log_file


def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name: Name for the logger, typically __name__
        
    Returns:
        logging.Logger: Configured logger
    """
    return logging.getLogger(name)


# If run directly, just set up logging
if __name__ == "__main__":
    log_file = configure_logging()
    logger = get_logger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    print(f"Log file created at: {log_file}")

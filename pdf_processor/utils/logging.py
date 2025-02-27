#!/usr/bin/env python3
"""
Logging Configuration Module

This module provides a centralized logging configuration for all modules in the package.
It configures:
- Console output with colored formatting based on log level
- File output with detailed formatting including timestamps
- Customizable log levels for different environments
- Separate log files for each run with date-based naming
- Log rotation to prevent excessive disk usage
- Automatic cleanup of old log files

Usage:
    from pdf_processor.utils.logging import configure_logging, get_logger
    
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
import glob
import time
from logging.handlers import RotatingFileHandler
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


def cleanup_old_logs(log_dir, max_age_days=7, max_files=100):
    """
    Clean up old log files to prevent disk space issues.
    
    Args:
        log_dir: Directory containing log files
        max_age_days: Maximum age of log files in days (default: 7)
        max_files: Maximum number of log files to keep (default: 100)
    """
    # Check if there are logs to clean up
    log_files = glob.glob(os.path.join(log_dir, "pdf_processing_*.log"))
    
    if not log_files:
        return
    
    # Sort files by modification time (oldest first)
    log_files.sort(key=os.path.getmtime)
    
    # Remove old files by age
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    
    for log_file in log_files[:]:
        file_age = current_time - os.path.getmtime(log_file)
        if file_age > max_age_seconds:
            try:
                os.remove(log_file)
                log_files.remove(log_file)
            except (OSError, PermissionError) as e:
                # Just log to stdout since logger might not be configured yet
                print(f"Could not remove old log file {log_file}: {e}")
    
    # If we still have too many files, remove the oldest ones
    if len(log_files) > max_files:
        for log_file in log_files[:(len(log_files) - max_files)]:
            try:
                os.remove(log_file)
            except (OSError, PermissionError) as e:
                print(f"Could not remove excess log file {log_file}: {e}")


def configure_logging(console_level=logging.INFO, file_level=logging.DEBUG, 
                     max_log_size_mb=10, backup_count=5, max_age_days=7):
    """
    Configure logging for the application.
    
    Args:
        console_level: Logging level for console output (default: INFO)
        file_level: Logging level for file output (default: DEBUG)
        max_log_size_mb: Maximum size of log files in MB before rotation (default: 10)
        backup_count: Number of backup files to keep when rotating (default: 5)
        max_age_days: Maximum age of log files in days (default: 7)
        
    Returns:
        str: Path to the main log file
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Clean up old log files
    cleanup_old_logs(log_dir, max_age_days)
    
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
    
    # Create file handler with detailed output and rotation
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Convert MB to bytes for the RotatingFileHandler
    max_bytes = max_log_size_mb * 1024 * 1024
    
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(file_format)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Log that logging has been configured
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Log file: {log_file}")
    
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
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    print(f"Log file created at: {log_file}")

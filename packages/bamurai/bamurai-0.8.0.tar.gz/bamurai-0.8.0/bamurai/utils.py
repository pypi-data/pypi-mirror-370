import time
import logging
from bamurai.logging_config import LOGGING_FORMAT, LOGGING_DATEFMT

def print_elapsed_time_pretty(start_time, logger=None):
    """Log elapsed time in a pretty format."""
    elapsed_time = time.time() - start_time

    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    if minutes < 1:
        seconds = round(elapsed_time, 2)
    else:
        seconds = int(elapsed_time % 60)

    if logger is None:
        logger = logging.getLogger("bamurai.utils")

    # below 5 minutes log in seconds
    if elapsed_time < 300:
        logger.info("Time taken: %ss", seconds)
    # below 1 hour log in minutes and seconds
    elif elapsed_time < 3600:
        logger.info("Time taken: %dm %ds", minutes, seconds)
    # above 1 hour log in hours, minutes and seconds
    else:
        logger.info("Time elapsed: %dh %dm %ds", hours, minutes, seconds)

def is_fastq(path):
    """Check if a file is a FASTQ file."""
    path = path.lower()
    return path.endswith(".fastq") or \
        path.endswith(".fq") or \
        path.endswith(".fastq.gz") or \
        path.endswith(".fq.gz")

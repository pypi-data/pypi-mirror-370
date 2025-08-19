# utils/logging_utils.py
import logging
import sys

def setup_logging(level="INFO"):
    """Configure logging with the specified level"""
    fmt = "%(asctime)s %(levelname)s %(name)s │ %(message)s"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    logging.root.setLevel(level)
    logging.root.addHandler(handler)
    return logging.getLogger()
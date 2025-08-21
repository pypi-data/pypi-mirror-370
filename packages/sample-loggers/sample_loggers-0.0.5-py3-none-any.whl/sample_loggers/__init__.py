import os
import logging

from yacs.config import CfgNode

from .logger import create_logger
from .utils import summery_model, throughput
from .version import __version__ as __version__


LEVEL = CfgNode()
LEVEL.DEBUG = logging.DEBUG
LEVEL.INFO = logging.INFO
LEVEL.WARNING = logging.WARNING
LEVEL.WARN = logging.WARN
LEVEL.ERROR = logging.ERROR
LEVEL.CRITICAL = logging.CRITICAL

LOG_FILE_NAME = os.environ.get("LOG_FILE_NAME", "log.txt")
LOG_DIR = os.environ.get("LOG_DIR", "./output/log")

logger = create_logger(
    logger_name="logger",
    log_level=LEVEL.DEBUG,
    log_file_name=LOG_FILE_NAME,
    output_dir=LOG_DIR,
)


__all__ = [
    '__version__',
    'create_logger',
    'logger',
    'summery_model',
    'throughput',
    'LEVEL',
]
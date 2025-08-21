import os
import logging
from . import logger

logger.set_logging_level(os.environ.get("ELASTIC_LOG_LEVEL", "INFO"))
if not logging.getLogger().hasHandlers():
    logger._set_console_handler()

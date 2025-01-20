"""
Module for logging setup.
"""

import logging
import os
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)

logger = logging.getLogger(__name__)

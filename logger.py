"""
"""

import logging
import os
import warnings  # Import warnings module to suppress warnings

# Suppress FutureWarnings globally
warnings.filterwarnings("ignore", category=FutureWarning)

# Logging setup
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


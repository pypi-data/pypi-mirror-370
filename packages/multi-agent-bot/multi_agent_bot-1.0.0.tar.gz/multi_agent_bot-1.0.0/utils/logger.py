import logging
import sys
import os

# Create logs directory if it doesn't exist
log_dir = "/tmp"
os.makedirs(log_dir, exist_ok=True)

# Configure logging with both stdout and file handlers
handlers = [
    logging.StreamHandler(sys.stdout),
    logging.FileHandler(f"{log_dir}/productbot.log", mode='a')
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers,
)

logger = logging.getLogger("productbot")
logger.setLevel(logging.DEBUG)

# Log startup message
logger.info("=== SOYBOT LOGGER INITIALIZED ===")
logger.info(f"Logging to: {log_dir}/productbot.log")

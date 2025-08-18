import logging

# Configure the default log level and format for the logger
logging.basicConfig(
    level=logging.DEBUG,  # Default log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
)

# Alias for the logging module to simulate `logPublisher` behavior
logPublisher = logging

# Exported logPublisher
__all__ = ["logPublisher"]
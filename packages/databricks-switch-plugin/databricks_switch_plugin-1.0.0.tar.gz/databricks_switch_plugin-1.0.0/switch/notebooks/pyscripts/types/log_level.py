"""Logging level definitions for Switch operations."""
from enum import Enum


class LogLevel(str, Enum):
    """Logging levels for Switch operations
    
    This enum defines the supported logging levels for debugging and monitoring.
    These levels control the verbosity of output during execution.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    @classmethod
    def get_supported_levels(cls) -> list[str]:
        """Get list of supported log level values
        
        Returns:
            List of supported log level names
        """
        return [level.value for level in cls]
